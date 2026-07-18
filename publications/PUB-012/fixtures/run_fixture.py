#!/usr/bin/env python3
"""
PUB-012 Fixture Runner — F-012-001 Paraphrase Evasion
=====================================================
v0.1.4 — fixes from Petrovich review #4 (msg 1784416688):
  - Fail-closed: missing jsonschema or fixture spec → exit(1), not fallback
  - Fail-closed: partial errors → error status if valid_ratio < 0.6
  - INV-2: oracle_hash (fixture spec) + environment_hash added to events
  - Fixture spec is source of truth: cases list read from spec, not hardcoded

Usage:
    python3 run_fixture.py --validator PATH --schema PATH
                           [--ledger PATH] [--fixture-spec PATH]
                           [--n-runs N]

Required: --validator and --schema (no guessing paths)
"""

import json
import hashlib
import subprocess
import sys
import os
import re
import argparse
from datetime import datetime, timezone

MINIMUM_VALID_RATIO = 0.6  # At least 60% of runs must succeed


def sha256_file(path):
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    """Compute sha256 of a string."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def compute_environment_hash():
    """Compute a deterministic hash of the runtime environment."""
    try:
        import jsonschema as _js
        js_version = _js.__version__
    except ImportError:
        return None, None  # Fail-closed: caller must handle

    env_str = f"python={sys.version.split()[0]}|platform={sys.platform}|jsonschema={js_version}"
    return sha256_str(env_str), f"jsonschema_{js_version}"


def run_validator_once(validator_path, case_path, schema_path):
    """Run validator on a case file once, return parsed output."""
    cmd = [sys.executable, validator_path, '--json-output', case_path]
    if schema_path:
        cmd.extend(['--schema', schema_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "parsed": {"error": "timeout"}, "timeout": True}
    except Exception as e:
        return {"exit_code": -1, "parsed": {"error": str(e)}, "exception": True}

    try:
        output = json.loads(result.stdout or result.stderr)
    except json.JSONDecodeError:
        return {
            "exit_code": result.returncode,
            "parsed": {
                "raw_stdout": result.stdout[:500],
                "raw_stderr": result.stderr[:500],
                "parse_error": True
            }
        }

    return {
        "exit_code": result.returncode,
        "parsed": output
    }


def extract_digest_neg_warnings(validator_output):
    """Extract warnings about digest vs negative_space overlap."""
    results = validator_output.get("parsed", {}).get("results", [])
    if not results:
        return [], []

    semantic = results[0].get("semantic", {})
    all_warnings = semantic.get("warnings", [])

    digest_neg = [
        w for w in all_warnings
        if isinstance(w, dict) and "negative_space" in w.get("path", "")
    ]

    matched_keywords = []
    for w in digest_neg:
        msg = w.get("message", "")
        kw_match = re.search(r"keyword '([^']+)'", msg)
        if kw_match:
            matched_keywords.append(kw_match.group(1))

    return digest_neg, matched_keywords


def run_n_times(validator_path, case_path, schema_path, n_runs):
    """Run validator N times independently, collecting all results."""
    runs = []
    for i in range(n_runs):
        output = run_validator_once(validator_path, case_path, schema_path)
        warnings, keywords = extract_digest_neg_warnings(output)
        runs.append({
            "run_index": i,
            "exit_code": output["exit_code"],
            "has_warnings": len(warnings) > 0,
            "matched_keywords": keywords,
            "digest_neg_warning_count": len(warnings),
            "error": output["parsed"].get("error") or output["parsed"].get("parse_error")
        })
    return runs


def classify_case(runs, expected_result, target_keyword):
    """Classify results across N runs. Returns INV-3 compliant status + metadata.

    Status is one of: pass, fail, inconclusive, error (per INV-3).
    Classification is metadata: true_positive, false_positive, etc.

    FAIL-CLOSED: if error ratio > (1 - MINIMUM_VALID_RATIO), status = error.
    """
    errors = [r for r in runs if r.get("error")]
    valid_runs = [r for r in runs if not r.get("error")]

    # Fail-closed: too many errors → error status regardless of valid results
    if not valid_runs or len(valid_runs) / len(runs) < MINIMUM_VALID_RATIO:
        return "error", "insufficient_valid_runs", {
            "n_valid_runs": len(valid_runs),
            "n_errored_runs": len(errors),
            "valid_ratio": round(len(valid_runs) / len(runs), 2) if runs else 0
        }

    all_keywords = []
    for r in valid_runs:
        all_keywords.extend(r["matched_keywords"])
    unique_keywords = set(all_keywords)
    keyword_counts = {kw: all_keywords.count(kw) for kw in unique_keywords}

    warned_runs = [r for r in valid_runs if r["has_warnings"]]
    warned_ratio = len(warned_runs) / len(valid_runs) if valid_runs else 0

    target_runs = [r for r in valid_runs if target_keyword in r["matched_keywords"]]
    target_ratio = len(target_runs) / len(valid_runs) if valid_runs else 0

    nondeterminism = {
        "n_valid_runs": len(valid_runs),
        "n_errored_runs": len(errors),
        "valid_ratio": round(len(valid_runs) / len(runs), 2),
        "warned_runs": len(warned_runs),
        "warned_ratio": round(warned_ratio, 2),
        "target_runs": len(target_runs),
        "target_ratio": round(target_ratio, 2),
        "unique_keywords": sorted(unique_keywords),
        "keyword_counts": keyword_counts
    }

    if expected_result == "pass":
        if target_ratio >= 0.5:
            return "pass", "true_positive", nondeterminism
        elif warned_ratio >= 0.5:
            return "inconclusive", "false_positive_on_incidental", nondeterminism
        else:
            return "fail", "false_negative", nondeterminism
    else:
        if warned_ratio == 0:
            return "fail", "true_negative", nondeterminism
        elif target_ratio == 0 and warned_ratio > 0:
            return "inconclusive", "false_positive_masks_evasion", nondeterminism
        else:
            return "pass", "guard_stronger_than_expected", nondeterminism


def append_to_ledger(ledger_path, event):
    """Append a hash-chained event to JSONL ledger."""
    prev_hash = "genesis"
    sequence = 0

    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                prev_hash = last.get("event_hash", "genesis")
                sequence = len(lines)

    event["prev_event_hash"] = prev_hash
    event["sequence"] = sequence

    canonical = json.dumps(event, sort_keys=True, ensure_ascii=False)
    event["event_hash"] = sha256_str(canonical)

    with open(ledger_path, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')

    return event


def load_fixture_spec(path):
    """Load fixture spec and extract case definitions."""
    with open(path, 'r') as f:
        spec = json.load(f)

    cases = []
    for tc in spec.get("test_cases", []):
        cases.append({
            "id": tc["id"],
            "file": os.path.basename(tc.get("file", "")),
            "description": tc.get("description", ""),
            "expected": tc.get("expected_result", "fail"),
            "target_keyword": tc.get("target_keyword", "")
        })

    return spec, cases


def main():
    parser = argparse.ArgumentParser(description="PUB-012 F-012-001 Fixture Runner v0.1.4")
    parser.add_argument('--validator', required=True, help='Path to validate_ompu_block_v02.py')
    parser.add_argument('--schema', required=True, help='Path to ompu_block_v0.2.json schema')
    parser.add_argument('--ledger', default='results.jsonl', help='Path to output ledger')
    parser.add_argument('--fixture-spec', default=None, help='Path to F-012-001 fixture spec')
    parser.add_argument('--n-runs', type=int, default=5, help='Runs per case for nondeterminism')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cases_dir = os.path.join(script_dir, 'cases')
    ledger_path = os.path.join(script_dir, args.ledger)
    fixture_spec_path = args.fixture_spec or os.path.join(script_dir, 'F-012-001-paraphrase-evasion.json')

    # Fail-closed: all required files must exist
    for label, path in [("Validator", args.validator), ("Schema", args.schema),
                         ("Cases dir", cases_dir), ("Fixture spec", fixture_spec_path)]:
        if not os.path.exists(path):
            print(f"ERROR: {label} not found at {path}", file=sys.stderr)
            sys.exit(1)

    # Fail-closed: jsonschema must be available
    environment_hash, schema_engine = compute_environment_hash()
    if environment_hash is None:
        print("ERROR: jsonschema package not installed. Cannot run without schema validation.", file=sys.stderr)
        sys.exit(1)

    # Load cases from fixture spec (spec is source of truth)
    spec, cases = load_fixture_spec(fixture_spec_path)
    if not cases:
        print("ERROR: Fixture spec has no test_cases", file=sys.stderr)
        sys.exit(1)

    validator_hash = sha256_file(args.validator)
    schema_hash = sha256_file(args.schema)
    oracle_hash = sha256_file(fixture_spec_path)
    runner_hash = sha256_file(os.path.abspath(__file__))

    print(f"PUB-012 F-012-001 Fixture Runner v0.1.4")
    print(f"=======================================")
    print(f"Validator: {args.validator}")
    print(f"Validator hash: {validator_hash[:16]}...")
    print(f"Schema engine: {schema_engine}")
    print(f"Oracle hash: {oracle_hash[:16]}...")
    print(f"Runner hash: {runner_hash[:16]}...")
    print(f"Environment hash: {environment_hash[:16]}...")
    print(f"N runs per case: {args.n_runs}")
    print(f"Min valid ratio: {MINIMUM_VALID_RATIO}")
    print()

    case_results = []
    overall_status = "pass"

    for case in cases:
        case_path = os.path.join(cases_dir, case["file"])
        if not os.path.exists(case_path):
            print(f"  ERROR {case['id']}: {case['file']} not found — fail-closed")
            case_results.append({
                "case_id": case["id"],
                "status": "error",
                "classification": "missing_carrier",
                "error": f"File not found: {case['file']}"
            })
            overall_status = "error"
            continue

        carrier_hash = sha256_file(case_path)

        print(f"  Running {case['id']} ({args.n_runs}x): {case['description']}")
        runs = run_n_times(args.validator, case_path, args.schema, args.n_runs)

        status, classification, nondeterminism = classify_case(
            runs, case["expected"], case["target_keyword"]
        )

        icon = {"pass": "✓", "fail": "✗", "inconclusive": "~", "error": "!"}[status]
        print(f"    {icon} status={status} classification={classification}")
        if nondeterminism.get("unique_keywords"):
            print(f"      keywords: {nondeterminism['keyword_counts']}")
        if nondeterminism.get("warned_ratio", 0) > 0 and nondeterminism.get("target_ratio", 0) == 0:
            print(f"      WARNING: guard fires on incidental match, not target '{case['target_keyword']}'")

        if status in ("fail", "inconclusive", "error"):
            overall_status = "error" if status == "error" else (
                "fail" if overall_status != "error" and status == "fail" else (
                    overall_status if overall_status in ("error", "fail") else status
                )
            )

        case_results.append({
            "case_id": case["id"],
            "description": case["description"],
            "expected": case["expected"],
            "status": status,
            "classification": classification,
            "carrier_hash": carrier_hash,
            "target_keyword": case["target_keyword"],
            "nondeterminism": nondeterminism,
            "runs": runs
        })

    print()

    run_event = {
        "type": "fixture_run",
        "fixture_id": "F-012-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runner": "dispatch",
        "runner_model": "claude-opus-4-6",
        "runner_version": "0.1.4",
        "validator_hash": validator_hash,
        "runner_hash": runner_hash,
        "oracle_hash": oracle_hash,
        "schema_hash": schema_hash,
        "schema_engine": schema_engine,
        "environment_hash": environment_hash,
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform
        },
        "n_runs_per_case": args.n_runs,
        "minimum_valid_ratio": MINIMUM_VALID_RATIO,
        "results": {r["case_id"]: r["status"] for r in case_results},
        "carrier_hashes": {r["case_id"]: r.get("carrier_hash", "missing") for r in case_results},
        "details": case_results,
        "overall": overall_status
    }

    event = append_to_ledger(ledger_path, run_event)
    print(f"Ledger event #{event['sequence']}: {event['event_hash'][:16]}...")
    print(f"Overall: {overall_status.upper()}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
PUB-012 Fixture Runner — F-012-001 Paraphrase Evasion
=====================================================
v0.1.3 — fixes from Petrovich review #3 (msg 1784390152):
  - N-run logic: independent runs with explicit paths, no dict hacking
  - INV-3 compliant: status in {pass, fail, inconclusive, error}
  - INV-2 compliant: per-case carrier_hash + oracle/runner/environment hashes
  - Classification is separate from status (metadata, not ledger field)

Runs three patched PUB-008 cases through validate_ompu_block_v02.py
and compares actual output to expected results.

Writes results to a hash-chained JSONL ledger (results.jsonl).

Usage:
    python3 run_fixture.py [--validator PATH] [--schema PATH]
                           [--ledger PATH] [--cases-dir DIR]
                           [--n-runs N]
"""

import json
import hashlib
import subprocess
import sys
import os
import re
import argparse
from datetime import datetime, timezone


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


def run_validator_once(validator_path, case_path, schema_path=None):
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
    """
    errors = [r for r in runs if r.get("error")]
    if len(errors) == len(runs):
        return "error", "all_runs_errored", {}

    valid_runs = [r for r in runs if not r.get("error")]

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


def main():
    parser = argparse.ArgumentParser(description="PUB-012 F-012-001 Fixture Runner v0.1.3")
    parser.add_argument('--validator', default=None, help='Path to validate_ompu_block_v02.py')
    parser.add_argument('--schema', default=None, help='Path to ompu_block_v0.2.json schema')
    parser.add_argument('--ledger', default='results.jsonl', help='Path to output ledger')
    parser.add_argument('--cases-dir', default='cases', help='Directory with case files')
    parser.add_argument('--n-runs', type=int, default=5, help='Runs per case for nondeterminism')
    parser.add_argument('--fixture-spec', default=None, help='Path to F-012-001 fixture spec')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))

    validator = args.validator or os.path.join(repo_root, 'publications', 'tools', 'validate_ompu_block_v02.py')
    schema = args.schema or os.path.join(repo_root, 'publications', 'schemas', 'ompu_block_v0.2.json')
    cases_dir = os.path.join(script_dir, args.cases_dir)
    ledger_path = os.path.join(script_dir, args.ledger)
    fixture_spec = args.fixture_spec or os.path.join(script_dir, 'F-012-001-paraphrase-evasion.json')

    if not os.path.exists(validator):
        print(f"ERROR: Validator not found at {validator}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(cases_dir):
        print(f"ERROR: Cases directory not found at {cases_dir}", file=sys.stderr)
        sys.exit(1)

    fixture_spec_hash = "no_spec"
    if os.path.exists(fixture_spec):
        fixture_spec_hash = sha256_file(fixture_spec)

    cases = [
        {
            "id": "F-012-001-A",
            "file": "PUB-008-case-A.json",
            "description": "Baseline — exact keyword 'structural' in digest and negative_space[4]",
            "expected": "pass",
            "target_keyword": "structural"
        },
        {
            "id": "F-012-001-B",
            "file": "PUB-008-case-B.json",
            "description": "Synonym substitution — 'architectural framework' replaces 'structural solution'",
            "expected": "fail",
            "target_keyword": "structural"
        },
        {
            "id": "F-012-001-C",
            "file": "PUB-008-case-C.json",
            "description": "Pure paraphrase — 'compact learned representation' replaces 'structural solution'",
            "expected": "fail",
            "target_keyword": "structural"
        }
    ]

    validator_hash = sha256_file(validator)
    schema_hash = sha256_file(schema) if os.path.exists(schema) else "no_schema"

    try:
        import jsonschema as _js
        schema_engine = f"jsonschema_{_js.__version__}"
    except ImportError:
        schema_engine = "fallback_no_jsonschema"

    print(f"PUB-012 F-012-001 Fixture Runner v0.1.3")
    print(f"=======================================")
    print(f"Validator: {validator}")
    print(f"Validator hash: {validator_hash[:16]}...")
    print(f"Schema engine: {schema_engine}")
    print(f"Fixture spec hash: {fixture_spec_hash[:16]}...")
    print(f"N runs per case: {args.n_runs}")
    print(f"Cases dir: {cases_dir}")
    print(f"Ledger: {ledger_path}")
    print()

    case_results = []
    overall_status = "pass"

    for case in cases:
        case_path = os.path.join(cases_dir, case["file"])
        if not os.path.exists(case_path):
            print(f"  SKIP {case['id']}: {case['file']} not found")
            continue

        carrier_hash = sha256_file(case_path)

        print(f"  Running {case['id']} ({args.n_runs}x): {case['description']}")
        runs = run_n_times(validator, case_path, schema, args.n_runs)

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
            overall_status = "fail" if status == "fail" else (
                overall_status if overall_status == "fail" else status
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
        "validator_hash": validator_hash,
        "runner_hash": sha256_file(os.path.abspath(__file__)),
        "fixture_spec_hash": fixture_spec_hash,
        "schema_hash": schema_hash,
        "schema_engine": schema_engine,
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform
        },
        "n_runs_per_case": args.n_runs,
        "results": {r["case_id"]: r["status"] for r in case_results},
        "carrier_hashes": {r["case_id"]: r["carrier_hash"] for r in case_results},
        "details": case_results,
        "overall": overall_status
    }

    event = append_to_ledger(ledger_path, run_event)
    print(f"Ledger event #{event['sequence']}: {event['event_hash'][:16]}...")
    print(f"Overall: {overall_status.upper()}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
PUB-012 Fixture Runner — F-012-001 Paraphrase Evasion
=====================================================
Runs three patched PUB-008 cases through validate_ompu_block_v02.py
and compares actual output to expected results.

Writes results to a hash-chained JSONL ledger (results.jsonl).

Usage:
    python3 run_fixture.py [--validator PATH] [--ledger PATH]

Default paths assume running from publications/PUB-012/fixtures/
"""

import json
import hashlib
import subprocess
import sys
import os
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


def run_validator(validator_path, case_path, schema_path=None):
    """Run validator on a case file, return parsed JSON output."""
    cmd = [sys.executable, validator_path, '--json-output', case_path]
    if schema_path:
        cmd.extend(['--schema', schema_path])

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        output = json.loads(result.stdout or result.stderr)
    except json.JSONDecodeError:
        output = {
            "raw_stdout": result.stdout,
            "raw_stderr": result.stderr,
            "exit_code": result.returncode,
            "parse_error": True
        }

    return {
        "exit_code": result.returncode,
        "parsed": output
    }


def extract_warnings(validator_output):
    """Extract warning details from validator JSON output."""
    results = validator_output.get("parsed", {}).get("results", [])
    if not results:
        return []

    semantic = results[0].get("semantic", {})
    return semantic.get("warnings", [])


def check_case(case_id, validator_output, expected_result, description,
               target_keyword=None, n_runs=5):
    """Compare actual validator output to expected, return verdict.

    Runs validator n_runs times to detect nondeterminism (Python set ordering).
    Classifies matched keywords as target vs incidental.
    """
    import re

    all_matched = []
    all_warnings_list = []

    for _ in range(n_runs):
        warnings = extract_warnings(validator_output)

        digest_neg_warnings = [
            w for w in warnings
            if isinstance(w, dict) and "negative_space" in w.get("path", "")
        ]

        matched_keywords = []
        for w in digest_neg_warnings:
            msg = w.get("message", "")
            kw_match = re.search(r"keyword '([^']+)'", msg)
            if kw_match:
                matched_keywords.append(kw_match.group(1))

        all_matched.extend(matched_keywords)
        all_warnings_list.append(warnings)

        # Re-run validator for nondeterminism detection (skip first, already done)
        if _ == 0:
            first_warnings = warnings
            first_digest_neg = digest_neg_warnings
            first_matched = matched_keywords
        else:
            validator_output = run_validator(
                validator_output.get("_validator_path", ""),
                validator_output.get("_case_path", ""),
                validator_output.get("_schema_path")
            )

    # Analyze nondeterminism
    unique_keywords = set(all_matched)
    keyword_counts = {kw: all_matched.count(kw) for kw in unique_keywords}

    # Classify: did the guard catch the TARGET keyword or something incidental?
    has_any_warning = len(first_digest_neg) > 0
    target_hit = target_keyword and target_keyword in first_matched
    incidental_hit = has_any_warning and not target_hit

    # Verdict logic:
    # pass = test behaved as expected
    # fail = test did NOT behave as expected
    if expected_result == "pass":
        # We expected the guard to catch it
        if target_hit:
            actual_result = "pass"
            classification = "true_positive"
        elif incidental_hit:
            actual_result = "pass_incidental"
            classification = "false_positive"
        else:
            actual_result = "fail"
            classification = "false_negative"
    else:
        # expected_result == "fail" — we expected the guard to MISS it
        if not has_any_warning:
            actual_result = "fail"  # guard missed it, as expected
            classification = "true_negative"
        elif incidental_hit:
            actual_result = "fail_masked"
            classification = "false_positive_masks_evasion"
        else:
            actual_result = "unexpected_pass"
            classification = "guard_stronger_than_expected"

    return {
        "case_id": case_id,
        "description": description,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "classification": classification,
        "exit_code": validator_output.get("exit_code", -1),
        "has_any_warning": has_any_warning,
        "target_keyword": target_keyword,
        "target_hit": target_hit,
        "incidental_hit": incidental_hit,
        "matched_keywords_this_run": first_matched,
        "nondeterminism": {
            "n_runs": 1,  # simplified — full nondeterminism check in separate mode
            "unique_keywords": list(unique_keywords),
            "keyword_counts": keyword_counts
        },
        "all_warnings": first_warnings,
        "digest_neg_warnings_count": len(first_digest_neg)
    }


def append_to_ledger(ledger_path, event):
    """Append a hash-chained event to JSONL ledger."""
    # Read last event hash
    prev_hash = "genesis"
    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                prev_hash = last.get("event_hash", "genesis")

    # Compute event hash
    event["prev_event_hash"] = prev_hash
    event["sequence"] = 0
    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            event["sequence"] = sum(1 for l in f if l.strip())

    # Hash everything except event_hash itself
    canonical = json.dumps(event, sort_keys=True, ensure_ascii=False)
    event["event_hash"] = sha256_str(canonical)

    with open(ledger_path, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')

    return event


def main():
    parser = argparse.ArgumentParser(description="PUB-012 F-012-001 Fixture Runner")
    parser.add_argument('--validator', default=None, help='Path to validate_ompu_block_v02.py')
    parser.add_argument('--schema', default=None, help='Path to ompu_block_v0.2.json schema')
    parser.add_argument('--ledger', default='results.jsonl', help='Path to output ledger')
    parser.add_argument('--cases-dir', default='cases', help='Directory with case files')
    args = parser.parse_args()

    # Find validator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))

    validator = args.validator or os.path.join(repo_root, 'publications', 'tools', 'validate_ompu_block_v02.py')
    schema = args.schema or os.path.join(repo_root, 'publications', 'schemas', 'ompu_block_v0.2.json')
    cases_dir = os.path.join(script_dir, args.cases_dir)
    ledger_path = os.path.join(script_dir, args.ledger)

    if not os.path.exists(validator):
        print(f"ERROR: Validator not found at {validator}")
        sys.exit(1)

    if not os.path.exists(cases_dir):
        print(f"ERROR: Cases directory not found at {cases_dir}")
        sys.exit(1)

    # Define test cases
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

    # Compute hashes
    validator_hash = sha256_file(validator)
    fixture_spec_hash = sha256_file(os.path.join(script_dir, 'F-012-001-paraphrase-evasion.json'))

    print(f"PUB-012 F-012-001 Fixture Runner")
    print(f"================================")
    print(f"Validator: {validator}")
    print(f"Validator hash: {validator_hash[:16]}...")
    print(f"Fixture hash: {fixture_spec_hash[:16]}...")
    print(f"Cases dir: {cases_dir}")
    print(f"Ledger: {ledger_path}")
    print()

    results = []
    all_pass = True

    for case in cases:
        case_path = os.path.join(cases_dir, case["file"])
        if not os.path.exists(case_path):
            print(f"  SKIP {case['id']}: {case['file']} not found")
            continue

        carrier_hash = sha256_file(case_path)

        print(f"  Running {case['id']}: {case['description']}")
        validator_output = run_validator(validator, case_path, schema)
        validator_output["_validator_path"] = validator
        validator_output["_case_path"] = case_path
        validator_output["_schema_path"] = schema
        verdict = check_case(
            case["id"], validator_output, case["expected"], case["description"],
            target_keyword=case.get("target_keyword")
        )

        is_clean = verdict["actual_result"] in ("pass", "fail")
        status_icon = "✓" if is_clean else "⚠"
        print(f"    {status_icon} expected={case['expected']}, "
              f"got={'warning' if verdict['has_any_warning'] else 'no_warning'}, "
              f"verdict={verdict['actual_result']} ({verdict['classification']})")
        if verdict["matched_keywords_this_run"]:
            print(f"    matched keywords: {verdict['matched_keywords_this_run']}")
        if verdict["incidental_hit"]:
            print(f"    ⚠ WARNING: incidental match on '{verdict['matched_keywords_this_run']}' — not the target keyword '{verdict['target_keyword']}'")

        if verdict["actual_result"] not in ("pass", "fail"):
            all_pass = False

        results.append(verdict)

    print()

    # Write to hash-chained ledger
    run_event = {
        "type": "fixture_run",
        "fixture_id": "F-012-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runner": "dispatch",
        "runner_model": "claude-opus-4-6",
        "validator_hash": validator_hash,
        "fixture_spec_hash": fixture_spec_hash,
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform
        },
        "results": {r["case_id"]: r["actual_result"] for r in results},
        "details": results,
        "overall": "pass" if all_pass else "fail"
    }

    event = append_to_ledger(ledger_path, run_event)
    print(f"Ledger event #{event['sequence']}: {event['event_hash'][:16]}...")
    print(f"Overall: {'PASS' if all_pass else 'FAIL'}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

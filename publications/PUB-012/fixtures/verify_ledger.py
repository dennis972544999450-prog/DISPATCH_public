#!/usr/bin/env python3
"""
PUB-012 Ledger Verifier v0.1.4
===============================
Verifies hash-chain integrity, INV-2/INV-3 compliance, and anchored head.

Checks:
  1. Non-empty (empty ledger = error, not pass)
  2. Hash chain continuity
  3. Event hash correctness (recompute)
  4. INV-3 status compliance (all status values in {pass, fail, inconclusive, error})
  5. INV-2 hash binding (all 5 hashes required: validator, runner, oracle, schema, environment)
  6. INV-2 carrier hashes per case
  7. Sequence monotonicity
  8. Anchored head (if --head provided, verify final event hash matches)

Usage:
    python3 verify_ledger.py [results.jsonl] [--head HASH] [--strict]
"""

import json
import hashlib
import sys
import os
import argparse


def sha256_str(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


INV3_STATUSES = {"pass", "fail", "inconclusive", "error"}
INV2_REQUIRED_HASHES = ["validator_hash", "runner_hash", "oracle_hash", "schema_hash", "environment_hash"]


def verify_ledger(path, expected_head=None, strict=False):
    if not os.path.exists(path):
        print(f"ERROR: Ledger not found at {path}")
        return 1

    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    # Fail-closed: empty ledger is an error
    if not lines:
        print("ERROR: Empty ledger — nothing to verify")
        return 1

    events = []
    parse_errors = 0
    for i, line in enumerate(lines):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"  PARSE ERROR line {i}: {e}")
            parse_errors += 1

    if parse_errors:
        print(f"FAIL: {parse_errors} parse errors")
        return 1

    print(f"Ledger: {path}")
    print(f"Events: {len(events)}")
    print()

    errors = []
    warnings = []

    for i, event in enumerate(events):
        prefix = f"Event #{i}"

        # 1. Sequence monotonicity
        seq = event.get("sequence")
        if seq is None:
            errors.append(f"{prefix}: missing 'sequence' field")
        elif seq != i:
            errors.append(f"{prefix}: sequence={seq}, expected={i}")

        # 2. Hash chain
        prev = event.get("prev_event_hash", "")
        if i == 0:
            if prev != "genesis":
                errors.append(f"{prefix}: first event prev_event_hash should be 'genesis', got '{prev[:16]}...'")
        else:
            expected_prev = events[i - 1].get("event_hash", "")
            if prev != expected_prev:
                errors.append(f"{prefix}: chain broken — prev_event_hash={prev[:16]}... != previous event_hash={expected_prev[:16]}...")

        # 3. Event hash correctness
        stored_hash = event.get("event_hash")
        if not stored_hash:
            errors.append(f"{prefix}: missing 'event_hash'")
        else:
            check = dict(event)
            del check["event_hash"]
            canonical = json.dumps(check, sort_keys=True, ensure_ascii=False)
            recomputed = sha256_str(canonical)
            if recomputed != stored_hash:
                errors.append(f"{prefix}: hash mismatch — stored={stored_hash[:16]}..., recomputed={recomputed[:16]}...")

        # 4. INV-3 status compliance
        results = event.get("results", {})
        for case_id, status in results.items():
            if status not in INV3_STATUSES:
                errors.append(f"{prefix}: {case_id} status='{status}' not in INV-3 set {sorted(INV3_STATUSES)}")

        # 5. INV-2 hash bindings (strict: all 5 required, not just present but non-empty)
        if event.get("type") == "fixture_run":
            for field in INV2_REQUIRED_HASHES:
                val = event.get(field)
                if not val or val in ("PENDING", "no_spec", "no_schema"):
                    if strict:
                        errors.append(f"{prefix}: INV-2 field '{field}' missing or placeholder (strict mode)")
                    else:
                        # In non-strict mode, warn for oracle/environment, error for validator/runner/schema
                        if field in ("validator_hash", "runner_hash", "schema_hash"):
                            errors.append(f"{prefix}: INV-2 field '{field}' missing or placeholder")
                        else:
                            warnings.append(f"{prefix}: INV-2 field '{field}' missing or placeholder")

            # 6. Carrier hashes per case
            carrier_hashes = event.get("carrier_hashes", {})
            if not carrier_hashes:
                errors.append(f"{prefix}: no carrier_hashes map")
            else:
                for case_id in results:
                    if case_id not in carrier_hashes:
                        errors.append(f"{prefix}: {case_id} missing from carrier_hashes")
                    elif carrier_hashes[case_id] in ("missing", "PENDING", ""):
                        errors.append(f"{prefix}: {case_id} carrier_hash is placeholder")

            # Check schema_engine is not fallback
            engine = event.get("schema_engine", "")
            if engine.startswith("fallback"):
                errors.append(f"{prefix}: schema_engine='{engine}' — jsonschema not available at runtime")

        # 7. Timestamp present
        ts = event.get("timestamp")
        if not ts:
            warnings.append(f"{prefix}: missing timestamp")

    # 8. Anchored head check
    if expected_head:
        actual_head = events[-1].get("event_hash", "")
        if actual_head != expected_head:
            errors.append(f"Anchored head mismatch: expected={expected_head[:16]}..., actual={actual_head[:16]}...")
        else:
            print(f"Anchored head: ✓ ({actual_head[:16]}...)")

    # Print results
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ~ {w}")

    print()
    chain_ok = not any("chain broken" in e for e in errors)
    hash_ok = not any("hash mismatch" in e for e in errors)
    inv3_ok = not any("INV-3" in e for e in errors)
    inv2_ok = not any("INV-2" in e for e in errors)

    print(f"Chain integrity: {'✓' if chain_ok else '✗'}")
    print(f"Hash correctness: {'✓' if hash_ok else '✗'}")
    print(f"INV-3 compliance: {'✓' if inv3_ok else '✗'}")
    print(f"INV-2 bindings: {'✓' if inv2_ok else '✗'}")
    print(f"Total errors: {len(errors)}")
    print(f"Total warnings: {len(warnings)}")

    if errors:
        print(f"\nVERDICT: FAIL ({len(errors)} errors)")
        return 1
    elif warnings:
        print(f"\nVERDICT: PASS with {len(warnings)} warnings")
        return 0
    else:
        print(f"\nVERDICT: PASS (clean)")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PUB-012 Ledger Verifier v0.1.4")
    parser.add_argument('ledger', nargs='?', default='results.jsonl', help='Path to ledger file')
    parser.add_argument('--head', default=None, help='Expected hash of final event (anchored head)')
    parser.add_argument('--strict', action='store_true', help='All INV-2 hashes required (not just core 3)')
    args = parser.parse_args()

    sys.exit(verify_ledger(args.ledger, args.head, args.strict))

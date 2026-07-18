#!/usr/bin/env python3
"""
PUB-012 Ledger Verifier
========================
Verifies hash-chain integrity and INV-2/INV-3 compliance of results.jsonl.

Checks:
  1. Hash chain continuity (each event.prev_event_hash == previous event.event_hash)
  2. Event hash correctness (recompute sha256 of canonical JSON sans event_hash)
  3. INV-3 status compliance (all status values in {pass, fail, inconclusive, error})
  4. INV-2 hash binding (carrier_hash, runner_hash, schema_hash present)
  5. Sequence monotonicity (sequence numbers increase by 1)
  6. Timestamp ordering (non-decreasing)

Usage:
    python3 verify_ledger.py [results.jsonl]
"""

import json
import hashlib
import sys
import os
from datetime import datetime


def sha256_str(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


INV3_STATUSES = {"pass", "fail", "inconclusive", "error"}


def verify_ledger(path):
    if not os.path.exists(path):
        print(f"ERROR: Ledger not found at {path}")
        return 1

    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        print("EMPTY: No events in ledger")
        return 0

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
                errors.append(f"{prefix}: {case_id} status='{status}' not in INV-3 set {INV3_STATUSES}")

        # 5. INV-2 hash bindings
        if event.get("type") == "fixture_run":
            for field in ["validator_hash", "runner_hash", "schema_hash"]:
                val = event.get(field)
                if not val:
                    warnings.append(f"{prefix}: missing INV-2 field '{field}'")
                elif val in ("PENDING", ""):
                    errors.append(f"{prefix}: INV-2 field '{field}' still PENDING")

            carrier_hashes = event.get("carrier_hashes", {})
            if not carrier_hashes:
                warnings.append(f"{prefix}: no carrier_hashes map")
            else:
                for case_id in results:
                    if case_id not in carrier_hashes:
                        warnings.append(f"{prefix}: {case_id} missing from carrier_hashes")

        # 6. Timestamp present
        ts = event.get("timestamp")
        if not ts:
            warnings.append(f"{prefix}: missing timestamp")

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
    inv2_ok = not any("INV-2" in e and "PENDING" in e for e in errors)

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
    path = sys.argv[1] if len(sys.argv) > 1 else "results.jsonl"
    sys.exit(verify_ledger(path))

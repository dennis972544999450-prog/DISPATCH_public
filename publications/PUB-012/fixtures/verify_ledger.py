#!/usr/bin/env python3
"""
PUB-012 Ledger Verifier v0.1.5
===============================
Verifies hash-chain integrity, INV-2/INV-3 compliance, and anchored head.

Changes from v0.1.4:
  - Legacy-aware: events without runner_version or < 0.1.4 get relaxed INV-2
    checks (warnings not errors) unless --strict overrides
  - Artifact recompute: --verify-artifacts with --validator/--schema/--spec/--cases-dir
    recomputes all hashes and compares against event fields
  - Pre-append gate: verify_for_append() checks full chain before new event

Checks:
  1. Non-empty (empty ledger = error, not pass)
  2. Hash chain continuity
  3. Event hash correctness (recompute)
  4. INV-3 status compliance (all status values in {pass, fail, inconclusive, error})
  5. INV-2 hash binding (all 5 hashes required for compliant events)
  6. INV-2 carrier hashes per case (shape + cross-reference)
  7. Sequence monotonicity
  8. Anchored head (if --head provided)
  9. Artifact recompute (if --verify-artifacts)

Usage:
    python3 verify_ledger.py [results.jsonl] [--head HASH] [--strict]
                             [--strict-from VERSION]
                             [--verify-artifacts --validator PATH --schema PATH
                              --spec PATH --cases-dir PATH]
"""

import json
import hashlib
import sys
import os
import re
import argparse


def sha256_str(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def sha256_file(path):
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


INV3_STATUSES = {"pass", "fail", "inconclusive", "error"}
INV2_REQUIRED_HASHES = ["validator_hash", "runner_hash", "oracle_hash", "schema_hash", "environment_hash"]
HEX64_PATTERN = re.compile(r'^[0-9a-f]{64}$')

# Events before this version get relaxed INV-2 checks (warnings not errors)
DEFAULT_COMPLIANCE_VERSION = "0.1.4"


def version_gte(version_str, threshold):
    """Compare version strings. Missing/None = pre-compliance."""
    if not version_str:
        return False
    try:
        v_parts = [int(x) for x in version_str.replace('b', '.').split('.')]
        t_parts = [int(x) for x in threshold.replace('b', '.').split('.')]
        return v_parts >= t_parts
    except (ValueError, AttributeError):
        return False


def verify_ledger(path, expected_head=None, strict=False, strict_from=None,
                  verify_artifacts=False, artifact_paths=None):
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

    compliance_version = strict_from or DEFAULT_COMPLIANCE_VERSION

    print(f"Ledger: {path}")
    print(f"Events: {len(events)}")
    print(f"Compliance threshold: {compliance_version}")
    print()

    errors = []
    warnings = []

    # Compute artifact hashes if requested
    artifact_hashes = {}
    if verify_artifacts and artifact_paths:
        print("Artifact recompute:")
        for label, apath in artifact_paths.items():
            if apath and os.path.exists(apath):
                h = sha256_file(apath)
                artifact_hashes[label] = h
                print(f"  {label}: {h[:16]}...")
            elif apath:
                errors.append(f"Artifact not found: {label} at {apath}")
                print(f"  {label}: NOT FOUND at {apath}")
        print()

    for i, event in enumerate(events):
        prefix = f"Event #{i}"
        runner_version = event.get("runner_version")
        is_compliant = version_gte(runner_version, compliance_version)

        version_tag = f" (v{runner_version})" if runner_version else " (pre-compliance)"

        # 1. Sequence monotonicity
        seq = event.get("sequence")
        if seq is None:
            errors.append(f"{prefix}{version_tag}: missing 'sequence' field")
        elif seq != i:
            errors.append(f"{prefix}{version_tag}: sequence={seq}, expected={i}")

        # 2. Hash chain
        prev = event.get("prev_event_hash", "")
        if i == 0:
            if prev != "genesis":
                errors.append(f"{prefix}{version_tag}: first event prev_event_hash should be 'genesis', got '{prev[:16]}...'")
        else:
            expected_prev = events[i - 1].get("event_hash", "")
            if prev != expected_prev:
                errors.append(f"{prefix}{version_tag}: chain broken — prev_event_hash={prev[:16]}... != previous event_hash={expected_prev[:16]}...")

        # 3. Event hash correctness
        stored_hash = event.get("event_hash")
        if not stored_hash:
            errors.append(f"{prefix}{version_tag}: missing 'event_hash'")
        else:
            check = dict(event)
            del check["event_hash"]
            canonical = json.dumps(check, sort_keys=True, ensure_ascii=False)
            recomputed = sha256_str(canonical)
            if recomputed != stored_hash:
                errors.append(f"{prefix}{version_tag}: hash mismatch — stored={stored_hash[:16]}..., recomputed={recomputed[:16]}...")

        # 4. INV-3 status compliance
        results = event.get("results", {})
        for case_id, status in results.items():
            if status not in INV3_STATUSES:
                if is_compliant:
                    errors.append(f"{prefix}{version_tag}: {case_id} status='{status}' not in INV-3 set {sorted(INV3_STATUSES)}")
                else:
                    warnings.append(f"{prefix}{version_tag}: {case_id} status='{status}' not in INV-3 set (pre-compliance)")

        # 5. INV-2 hash bindings: shape + presence
        if event.get("type") == "fixture_run":
            for field in INV2_REQUIRED_HASHES:
                val = event.get(field)
                if not val or val in ("PENDING", "no_spec", "no_schema"):
                    if strict or is_compliant:
                        errors.append(f"{prefix}{version_tag}: INV-2 field '{field}' missing or placeholder")
                    else:
                        warnings.append(f"{prefix}{version_tag}: INV-2 field '{field}' missing or placeholder (pre-compliance)")
                elif not HEX64_PATTERN.match(val):
                    errors.append(f"{prefix}{version_tag}: INV-2 field '{field}' is not valid sha256 (expected 64 hex chars, got '{val[:20]}...')")
                elif verify_artifacts and is_compliant:
                    # Artifact recompute comparison
                    artifact_key = field  # e.g. "validator_hash"
                    if artifact_key in artifact_hashes and val != artifact_hashes[artifact_key]:
                        errors.append(f"{prefix}{version_tag}: INV-2 {field} mismatch — event={val[:16]}... artifact={artifact_hashes[artifact_key][:16]}...")

            # 6. Carrier hashes per case — presence, shape, cross-reference
            carrier_hashes = event.get("carrier_hashes", {})
            if not carrier_hashes:
                if is_compliant:
                    errors.append(f"{prefix}{version_tag}: no carrier_hashes map")
                else:
                    warnings.append(f"{prefix}{version_tag}: no carrier_hashes map (pre-compliance)")
            else:
                for case_id in results:
                    if case_id not in carrier_hashes:
                        errors.append(f"{prefix}{version_tag}: {case_id} missing from carrier_hashes")
                    elif carrier_hashes[case_id] in ("missing", "PENDING", ""):
                        errors.append(f"{prefix}{version_tag}: {case_id} carrier_hash is placeholder")
                    elif not HEX64_PATTERN.match(carrier_hashes[case_id]):
                        errors.append(f"{prefix}{version_tag}: {case_id} carrier_hash is not valid sha256")
                    elif verify_artifacts and is_compliant:
                        # Check carrier hash against actual case file
                        case_file_key = f"carrier_{case_id}"
                        if case_file_key in artifact_hashes and carrier_hashes[case_id] != artifact_hashes[case_file_key]:
                            errors.append(f"{prefix}{version_tag}: {case_id} carrier_hash mismatch — event={carrier_hashes[case_id][:16]}... file={artifact_hashes[case_file_key][:16]}...")

                # Cross-reference: carrier_hashes in details[] must match top-level map
                details = event.get("details", [])
                for detail in details:
                    cid = detail.get("case_id")
                    detail_hash = detail.get("carrier_hash")
                    top_hash = carrier_hashes.get(cid)
                    if cid and detail_hash and top_hash and detail_hash != top_hash:
                        errors.append(f"{prefix}{version_tag}: {cid} carrier_hash mismatch: details={detail_hash[:16]}... vs top={top_hash[:16]}...")

            # Check schema_engine is not fallback
            engine = event.get("schema_engine", "")
            if engine.startswith("fallback"):
                errors.append(f"{prefix}{version_tag}: schema_engine='{engine}' — jsonschema not available at runtime")

        # 7. Timestamp present
        ts = event.get("timestamp")
        if not ts:
            warnings.append(f"{prefix}{version_tag}: missing timestamp")

    # 8. Anchored head check
    if expected_head:
        actual_head = events[-1].get("event_hash", "")
        if actual_head != expected_head:
            errors.append(f"Anchored head mismatch: expected={expected_head[:16]}..., actual={actual_head[:16]}...")
        else:
            print(f"Anchored head: ✓ ({actual_head[:16]}...)")

    # Print results
    legacy_count = sum(1 for e in events if not version_gte(e.get("runner_version"), compliance_version))
    compliant_count = len(events) - legacy_count
    print(f"Legacy events: {legacy_count}")
    print(f"Compliant events: {compliant_count}")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ~ {w}")

    print()
    chain_ok = not any("chain broken" in e for e in errors)
    hash_ok = not any("hash mismatch" in e and "INV-2" not in e for e in errors)
    inv3_ok = not any("INV-3" in e for e in errors)
    inv2_ok = not any("INV-2" in e for e in errors)
    artifact_ok = not any("artifact" in e.lower() for e in errors) if verify_artifacts else True

    print(f"Chain integrity: {'✓' if chain_ok else '✗'}")
    print(f"Hash correctness: {'✓' if hash_ok else '✗'}")
    print(f"INV-3 compliance: {'✓' if inv3_ok else '✗'}")
    print(f"INV-2 bindings: {'✓' if inv2_ok else '✗'}")
    if verify_artifacts:
        print(f"Artifact binding: {'✓' if artifact_ok else '✗'}")
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


def verify_for_append(ledger_path):
    """Pre-append gate: verify full chain before allowing new event.

    Returns (ok, head_hash, count) — caller should only append if ok=True.
    """
    if not os.path.exists(ledger_path):
        return True, "genesis", 0  # New ledger, genesis start

    with open(ledger_path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        return True, "genesis", 0

    prev_hash = "genesis"
    for i, line in enumerate(lines):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return False, None, i

        # Check sequence
        if event.get("sequence") != i:
            return False, None, i

        # Check chain
        if event.get("prev_event_hash") != prev_hash:
            return False, None, i

        # Verify event hash
        stored_hash = event.get("event_hash")
        if not stored_hash:
            return False, None, i

        check = dict(event)
        del check["event_hash"]
        canonical = json.dumps(check, sort_keys=True, ensure_ascii=False)
        recomputed = sha256_str(canonical)
        if recomputed != stored_hash:
            return False, None, i

        prev_hash = stored_hash

    return True, prev_hash, len(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PUB-012 Ledger Verifier v0.1.5")
    parser.add_argument('ledger', nargs='?', default='results.jsonl', help='Path to ledger file')
    parser.add_argument('--head', default=None, help='Expected hash of final event (anchored head)')
    parser.add_argument('--strict', action='store_true', help='All INV-2 hashes required even for legacy events')
    parser.add_argument('--strict-from', default=None,
                        help=f'Version threshold for compliance (default: {DEFAULT_COMPLIANCE_VERSION})')
    parser.add_argument('--verify-artifacts', action='store_true',
                        help='Recompute and compare hashes against actual artifact files')
    parser.add_argument('--validator', default=None, help='Path to validator (for --verify-artifacts)')
    parser.add_argument('--schema', default=None, help='Path to schema (for --verify-artifacts)')
    parser.add_argument('--spec', default=None, help='Path to fixture spec (for --verify-artifacts)')
    parser.add_argument('--cases-dir', default=None, help='Path to cases directory (for --verify-artifacts)')
    args = parser.parse_args()

    artifact_paths = {}
    if args.verify_artifacts:
        if not args.validator or not args.schema:
            print("ERROR: --verify-artifacts requires --validator and --schema", file=sys.stderr)
            sys.exit(1)
        artifact_paths["validator_hash"] = args.validator
        artifact_paths["schema_hash"] = args.schema
        if args.spec:
            artifact_paths["oracle_hash"] = args.spec
        # Compute carrier hashes for each case file
        cases_dir = args.cases_dir
        if not cases_dir and args.spec:
            cases_dir = os.path.join(os.path.dirname(args.spec), 'cases')
        if cases_dir and os.path.isdir(cases_dir):
            # Read spec to get case IDs and file mappings
            if args.spec and os.path.exists(args.spec):
                with open(args.spec) as f:
                    spec = json.load(f)
                for tc in spec.get("test_cases", []):
                    case_file = os.path.join(cases_dir, os.path.basename(tc.get("file", "")))
                    if os.path.exists(case_file):
                        artifact_paths[f"carrier_{tc['id']}"] = case_file

    sys.exit(verify_ledger(
        args.ledger, args.head, args.strict, args.strict_from,
        args.verify_artifacts, artifact_paths
    ))

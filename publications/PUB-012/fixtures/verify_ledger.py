#!/usr/bin/env python3
"""
PUB-012 Ledger Verifier v0.1.6
===============================
Verifies hash-chain integrity, INV-2/INV-3 compliance, and anchored head.

Changes from v0.1.5:
  - Complete artifact recompute: --verify-artifacts now requires --runner,
    --spec, --cases-dir in addition to --validator and --schema. Recomputes
    all 5 top-level hashes plus carrier hashes. Environment hash is verified
    via internal consistency (recomputed from event's own metadata fields).
    Previous partial mode removed.
  - Anchored legacy cutover: compliance boundary determined by POSITION of
    first compliant event in the chain (sequence number), not self-declared
    runner_version. Events after cutover are treated as compliant regardless
    of what they declare. Prevents version-downgrade bypass.
  - Environment hash internal consistency: recomputes environment_hash from
    event's own environment/schema_engine fields (not verifier's own env).

Checks:
  1. Non-empty (empty ledger = error, not pass)
  2. Hash chain continuity
  3. Event hash correctness (recompute)
  4. INV-3 status compliance (all status values in {pass, fail, inconclusive, error})
  5. INV-2 hash binding (all 5 hashes required for compliant events)
  6. INV-2 carrier hashes per case (shape + cross-reference)
  7. Sequence monotonicity
  8. Anchored head (if --head provided)
  9. Artifact recompute — complete mode (if --verify-artifacts)
  10. Anchored legacy cutover (position-based, not self-declared)
  11. Environment hash internal consistency (for compliant events)

Usage:
    python3 verify_ledger.py [results.jsonl] [--head HASH] [--strict]
                             [--strict-from VERSION]
                             [--verify-artifacts --validator PATH --schema PATH
                              --runner PATH --spec PATH --cases-dir PATH]
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


def find_cutover_sequence(events, compliance_version):
    """Find the sequence number where the chain first crossed compliance threshold.

    The geological layer cannot self-declare its age. Once the chain crosses
    the compliance boundary, all subsequent events are treated as compliant
    regardless of self-declared runner_version.

    Returns sequence number of first compliant event, or None if no compliant
    events exist yet.
    """
    for event in events:
        rv = event.get("runner_version")
        if version_gte(rv, compliance_version):
            return event.get("sequence")
    return None


def recompute_environment_hash(event):
    """Recompute environment_hash from event's own metadata fields.

    Uses the same formula as run_fixture.py:
      python={version}|platform={platform}|jsonschema={js_version}

    This is an internal consistency check: does the stored hash match
    what you'd get from the event's own environment and schema_engine fields?
    """
    env_data = event.get("environment", {})
    schema_engine = event.get("schema_engine", "")

    py_ver = env_data.get("python", "")
    plat = env_data.get("platform", "")

    if not (py_ver and plat and schema_engine):
        return None  # Not enough metadata to recompute

    # Extract jsonschema version from schema_engine field
    if schema_engine.startswith("jsonschema_"):
        js_ver = schema_engine[len("jsonschema_"):]
    else:
        return None  # Unrecognized engine format

    env_str = f"python={py_ver}|platform={plat}|jsonschema={js_ver}"
    return sha256_str(env_str)


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

    # Anchored cutover: find first compliant event by version declaration,
    # then anchor all subsequent events to that position
    cutover_seq = find_cutover_sequence(events, compliance_version)

    print(f"Ledger: {path}")
    print(f"Events: {len(events)}")
    print(f"Compliance threshold: {compliance_version}")
    if cutover_seq is not None:
        print(f"Cutover sequence: {cutover_seq} (events >= {cutover_seq} treated as compliant)")
    else:
        print(f"Cutover sequence: none (no compliant events found)")
    print()

    errors = []
    warnings = []

    # Compute artifact hashes if requested
    artifact_hashes = {}
    if verify_artifacts and artifact_paths:
        print("Artifact recompute (complete mode):")
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

        # Anchored compliance: position in chain determines compliance,
        # not self-declared runner_version
        if strict:
            is_compliant = True
        elif cutover_seq is not None and i >= cutover_seq:
            is_compliant = True
        else:
            is_compliant = False

        # Warn on version downgrade after cutover
        if is_compliant and runner_version and not version_gte(runner_version, compliance_version):
            warnings.append(
                f"{prefix}: sequence {i} >= cutover {cutover_seq} but "
                f"runner_version={runner_version} < {compliance_version} — "
                f"version downgrade after cutover (treated as compliant by position)"
            )

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

        # 5-6. INV-2 hash bindings (fixture_run events only)
        if event.get("type") == "fixture_run":
            for field in INV2_REQUIRED_HASHES:
                val = event.get(field)
                if not val or val in ("PENDING", "no_spec", "no_schema"):
                    if is_compliant:
                        errors.append(f"{prefix}{version_tag}: INV-2 field '{field}' missing or placeholder")
                    else:
                        warnings.append(f"{prefix}{version_tag}: INV-2 field '{field}' missing or placeholder (pre-compliance)")
                elif not HEX64_PATTERN.match(val):
                    errors.append(f"{prefix}{version_tag}: INV-2 field '{field}' is not valid sha256 (expected 64 hex chars, got '{val[:20]}...')")
                elif verify_artifacts and is_compliant:
                    # Artifact recompute: compare event hash against file hash
                    artifact_key = field
                    if artifact_key in artifact_hashes and val != artifact_hashes[artifact_key]:
                        errors.append(f"{prefix}{version_tag}: INV-2 {field} drift — event={val[:16]}... artifact={artifact_hashes[artifact_key][:16]}...")

            # 11. Environment hash internal consistency (for compliant events)
            if is_compliant:
                stored_env_hash = event.get("environment_hash")
                recomputed_env = recompute_environment_hash(event)
                if stored_env_hash and recomputed_env:
                    if stored_env_hash != recomputed_env:
                        errors.append(
                            f"{prefix}{version_tag}: environment_hash inconsistent with own metadata — "
                            f"stored={stored_env_hash[:16]}... recomputed={recomputed_env[:16]}..."
                        )

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
                            errors.append(f"{prefix}{version_tag}: {case_id} carrier_hash drift — event={carrier_hashes[case_id][:16]}... file={artifact_hashes[case_file_key][:16]}...")

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
    legacy_count = sum(1 for i, e in enumerate(events)
                       if cutover_seq is None or i < cutover_seq)
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
    artifact_ok = not any("drift" in e.lower() for e in errors) if verify_artifacts else True
    env_ok = not any("environment_hash inconsistent" in e for e in errors)

    print(f"Chain integrity: {'✓' if chain_ok else '✗'}")
    print(f"Hash correctness: {'✓' if hash_ok else '✗'}")
    print(f"INV-3 compliance: {'✓' if inv3_ok else '✗'}")
    print(f"INV-2 bindings: {'✓' if inv2_ok else '✗'}")
    if verify_artifacts:
        print(f"Artifact binding: {'✓' if artifact_ok else '✗'}")
    print(f"Environment consistency: {'✓' if env_ok else '✗'}")
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
    parser = argparse.ArgumentParser(description="PUB-012 Ledger Verifier v0.1.6")
    parser.add_argument('ledger', nargs='?', default='results.jsonl', help='Path to ledger file')
    parser.add_argument('--head', default=None, help='Expected hash of final event (anchored head)')
    parser.add_argument('--strict', action='store_true', help='All INV-2 hashes required even for legacy events')
    parser.add_argument('--strict-from', default=None,
                        help=f'Version threshold for compliance (default: {DEFAULT_COMPLIANCE_VERSION})')
    parser.add_argument('--verify-artifacts', action='store_true',
                        help='Complete artifact recompute — requires all five artifact paths')
    parser.add_argument('--validator', default=None, help='Path to validator script')
    parser.add_argument('--schema', default=None, help='Path to schema file')
    parser.add_argument('--runner', default=None, help='Path to runner script')
    parser.add_argument('--spec', default=None, help='Path to fixture spec')
    parser.add_argument('--cases-dir', default=None, help='Path to cases directory')
    args = parser.parse_args()

    artifact_paths = {}
    if args.verify_artifacts:
        missing = []
        for flag, name in [('validator', '--validator'), ('schema', '--schema'),
                           ('runner', '--runner'), ('spec', '--spec'),
                           ('cases_dir', '--cases-dir')]:
            if not getattr(args, flag):
                missing.append(name)
        if missing:
            print(f"ERROR: --verify-artifacts requires {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

        artifact_paths["validator_hash"] = args.validator
        artifact_paths["schema_hash"] = args.schema
        artifact_paths["runner_hash"] = args.runner
        artifact_paths["oracle_hash"] = args.spec

        # Compute carrier hashes for each case file from spec
        if os.path.exists(args.spec):
            with open(args.spec) as f:
                spec = json.load(f)
            cases_dir = args.cases_dir
            for tc in spec.get("test_cases", []):
                case_file = os.path.join(cases_dir, os.path.basename(tc.get("file", "")))
                if os.path.exists(case_file):
                    artifact_paths[f"carrier_{tc['id']}"] = case_file

    sys.exit(verify_ledger(
        args.ledger, args.head, args.strict, args.strict_from,
        args.verify_artifacts, artifact_paths
    ))

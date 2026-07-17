#!/usr/bin/env python3
"""Recompute locked PILOT-001 scores and output hashes without editing data."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "PILOT-001_results.json"
JUDGING = ROOT / "PILOT-001_blind_judging.json"


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def checks(response: dict[str, object]) -> dict[str, bool]:
    reactivate = set(response["reactivate"])
    reopen = set(response["demote_or_reopen"])
    preserve = set(response["preserve"])
    return {
        "P1-C01": "KEEP_ALL" in reactivate,
        "P1-C02": "ENVELOPE" in reopen,
        "P1-C03": response["public_action"] == "redact_then_publish",
        "P1-C04": {"ORIGINALS", "NO_EFFECT_DENOMINATOR"} <= preserve,
        "P1-C05": response["null_state"] == "no_tested_format_advantage",
        "P1-C06": response["decision_state"] == "bounded_uncertainty",
    }


def main() -> int:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    judging = json.loads(JUDGING.read_text(encoding="utf-8"))
    assert data["status"] == "complete_exploratory"
    assert len(data["runs"]) == 10
    by_arm: dict[str, list[int]] = defaultdict(list)
    for run in data["runs"]:
        assert run["denominator_included"] is True
        expected = checks(run["response"])
        assert expected == run["strict_checks"], run["run_id"]
        score = sum(expected.values())
        assert score == run["strict_total"], run["run_id"]
        assert canonical_hash(run["response"]) == run["output_sha256"], run["run_id"]
        by_arm[run["arm_id"]].append(score)
    assert all(len(values) == 2 for values in by_arm.values())
    for arm, values in sorted(by_arm.items()):
        mean = sum(values) / len(values)
        recorded = data["strict_summary"][arm]
        assert recorded == {"n": 2, "mean": mean, "scores": values}
        print(f"{arm}: n=2 scores={values} mean={mean:.1f}/6")
    judge_scores = [judge["scores"] for judge in judging["judges"]]
    assert len(judge_scores) == 2 and judge_scores[0] == judge_scores[1]
    blind_to_arm = {run["blind_id"]: run["arm_id"] for run in data["runs"]}
    semantic_by_arm: dict[str, list[int]] = defaultdict(list)
    for blind_id, score in judge_scores[0].items():
        semantic_by_arm[blind_to_arm[blind_id]].append(score)
    for arm, values in sorted(semantic_by_arm.items()):
        values.sort()
        recorded = data["semantic_summary"][arm]
        assert recorded == {"n": 2, "mean": sum(values) / 2, "scores": values}
    assert judging["agreement"]["binary_check_agreement"] == "60/60"
    print("OK: 10/10 runs retained; strict checks and output hashes exact; blind judges agree 60/60; P1-C03 remains flagged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

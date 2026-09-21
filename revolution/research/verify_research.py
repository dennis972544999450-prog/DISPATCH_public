#!/usr/bin/env python3
"""Strict structural, Git, and hash verifier for the revolution research layer."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
LEDGER_PATH = ROOT / "source_ledger.json"
TEXT_PROTOCOL_PATH = ROOT / "EX-001_text_grating_protocol.json"
BLOCK_PROTOCOL_PATH = ROOT / "EX-002_conversation_morphogenesis_protocol.json"
BLOCK_SCHEMA_PATH = ROOT / "block_envelope.schema.json"
BLOCK_EXAMPLE_PATH = ROOT / "block_envelope.example.json"
RUN_SCHEMA_PATH = ROOT / "run_result.schema.json"
PILOT_PROTOCOL_PATH = ROOT / "pilot" / "PILOT-001_block_reentry_protocol.json"
PILOT_RESULTS_PATH = ROOT / "pilot" / "PILOT-001_results.json"
PILOT_SCORE_PATH = ROOT / "pilot" / "score_pilot.py"
PILOT2_PROTOCOL_PATH = ROOT / "pilot" / "PILOT-002_block_rendering_protocol.json"
PILOT2_REQUESTS_PATH = ROOT / "pilot" / "PILOT-002_requests.json"
PILOT2_OUTPUTS_PATH = ROOT / "pilot" / "PILOT-002_outputs_blind.json"
PILOT2_ASSIGNMENT_PATH = ROOT / "pilot" / "PILOT-002_assignment.json"
PILOT2_JUDGES_PATH = ROOT / "pilot" / "PILOT-002_judges.json"
PILOT2_RESULTS_PATH = ROOT / "pilot" / "PILOT-002_results.json"
MANIFEST_PATH = ROOT / "bundle_manifest.json"

SOURCE_COMMIT = "b194b22ef315547053f1835755f05880d74da1f0"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
QUESTION_RE = re.compile(r"^REV:Q-00[1-6]$")
SOURCE_ID_RE = re.compile(r"^REV:SRC-[0-9]{3}$")

SCALE = {"rev:T1", "rev:T2", "rev:T3", "rev:T4"}
VERDICTS = {"bounded_support", "counterevidence", "reframed", "terminology_only", "unknown"}
NULLS = {
    "examined_no_effect",
    "failed_manipulation",
    "uninterpretable",
    "refusal",
    "missing",
    "excluded_with_reason",
    "never_sampled",
}
RUN_FIELDS = {
    "run_id",
    "protocol_id",
    "lane_id",
    "arm_id",
    "provider",
    "model",
    "model_fingerprint",
    "system_prompt_hash",
    "request_hash",
    "context_hash",
    "temperature",
    "top_p",
    "max_tokens",
    "seed",
    "request_time",
    "request_id",
    "tool_access_hash",
    "tool_trace_hash",
    "status",
    "exclusion_reason",
    "denominator_included",
    "output_hash",
    "artifact_receipt",
    "null_disposition",
}

EX2_LEVELS = {
    "prime_type": {"neutral", "lexical_A", "semantic_paraphrase_A"},
    "prime_lag": {"immediate", "matched_filler"},
    "selection_history": {"exposure_only", "choice_attributed_to_other", "self_selected"},
    "reopening": {"none", "diagnostic_evidence"},
    "payload": {"absent", "exact_B", "exact_B_plain_prose", "exact_B_shuffled_fields"},
    "carrier": {"none", "file", "inline"},
    "read_state": {"not_available", "unread", "read", "tool_read_exact_bytes"},
    "role_frame": {"helpful", "peer"},
    "response_policy": {"direct", "branch"},
    "request_hash": {"exact_R"},
    "provider_seed": {"A", "B", "unsupported_record_request_only"},
    "interaction_mode": {"A_only", "B_only", "A_plus_B_concatenated", "B0_to_A1_to_B1"},
}


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _exact_keys(value: Any, required: Iterable[str], label: str, optional: Iterable[str] = ()) -> None:
    _require(isinstance(value, dict), f"{label}: expected object")
    required_set = set(required)
    allowed = required_set | set(optional)
    actual = set(value)
    _require(required_set <= actual, f"{label}: missing keys {sorted(required_set - actual)}")
    _require(actual <= allowed, f"{label}: unknown keys {sorted(actual - allowed)}")


def _unique(values: Iterable[str], label: str) -> None:
    materialized = list(values)
    _require(all(isinstance(value, str) and value for value in materialized), f"{label}: empty id")
    _require(len(materialized) == len(set(materialized)), f"{label}: duplicate id")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _reject_constant(value: str) -> None:
    raise ValidationError(f"JSON: non-finite number {value}")


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"JSON: duplicate key {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=_strict_pairs, parse_constant=_reject_constant)
    _require(isinstance(value, dict), f"{path.name}: top-level value must be object")
    return value


def _validate_source(source: Any, label: str, counter: bool = False) -> None:
    required = {"title", "year", "url", "kind"}
    if counter:
        required.add("relation")
    _exact_keys(source, required, label)
    _require(isinstance(source["title"], str) and source["title"], f"{label}: missing title")
    _require(isinstance(source["year"], int) and not isinstance(source["year"], bool), f"{label}: invalid year")
    _require(1900 <= source["year"] <= 2100, f"{label}: implausible year")
    _require(isinstance(source["url"], str) and source["url"].startswith("https://"), f"{label}: URL must be HTTPS")
    _require(isinstance(source["kind"], str) and source["kind"], f"{label}: missing kind")
    if counter:
        _require(isinstance(source["relation"], str) and source["relation"], f"{label}: missing relation")


def validate_ledger(data: dict[str, Any]) -> None:
    _exact_keys(data, {"schema_version", "source_snapshot_commit", "evidence_scale", "claims"}, "ledger")
    _require(data["schema_version"] == "0.2", "ledger: unsupported schema_version")
    _require(data["source_snapshot_commit"] == SOURCE_COMMIT, "ledger: source snapshot mismatch")
    _require(set(data["evidence_scale"]) == SCALE and len(data["evidence_scale"]) == len(SCALE), "ledger: evidence scale mismatch")
    claims = data["claims"]
    _require(isinstance(claims, list) and claims, "ledger: claims must be non-empty")
    _unique((claim.get("id") for claim in claims), "ledger claims")
    for claim in claims:
        _exact_keys(
            claim,
            {"id", "questions", "claim", "strength", "verdict", "source", "shows", "does_not_show", "rivals"},
            claim.get("id", "ledger claim"),
            {"counter_sources"},
        )
        claim_id = claim["id"]
        _require(bool(SOURCE_ID_RE.fullmatch(claim_id)), f"{claim_id}: invalid namespaced id")
        _require(claim["strength"] in SCALE, f"{claim_id}: invalid strength")
        _require(claim["strength"] != "rev:T1", f"{claim_id}: T1 requires an explicit replication schema")
        _require(claim["verdict"] in VERDICTS, f"{claim_id}: invalid verdict")
        for field in ("claim", "shows", "does_not_show"):
            _require(isinstance(claim[field], str) and claim[field], f"{claim_id}: missing {field}")
        _require(isinstance(claim["questions"], list) and claim["questions"], f"{claim_id}: missing question links")
        _require(all(bool(QUESTION_RE.fullmatch(q)) for q in claim["questions"]), f"{claim_id}: invalid question link")
        _require(len(claim["questions"]) == len(set(claim["questions"])), f"{claim_id}: duplicate question link")
        _require(isinstance(claim["rivals"], list) and claim["rivals"], f"{claim_id}: missing rivals")
        _validate_source(claim["source"], f"{claim_id}.source")
        counters = claim.get("counter_sources", [])
        _require(isinstance(counters, list), f"{claim_id}: counter_sources must be list")
        for index, source in enumerate(counters):
            _validate_source(source, f"{claim_id}.counter_sources[{index}]", counter=True)


def validate_text_protocol(data: dict[str, Any]) -> None:
    required = {
        "schema_version", "protocol_id", "title", "status", "source_snapshot_commit", "objective",
        "non_claims", "primary_factor_levels", "fixed_features", "factorial_conditions",
        "secondary_controls", "primary_outcome", "primary_estimand", "measurement_plan", "sampling",
        "run_manifest_fields", "null_register", "forbidden_primary_proxies",
    }
    _exact_keys(data, required, "EX-001")
    _require(data["schema_version"] == "0.2" and data["protocol_id"] == "REV:EX-001", "EX-001: identity mismatch")
    _require(data["status"] == "pilot_design", "EX-001: status must be pilot_design")
    _require(data["source_snapshot_commit"] == SOURCE_COMMIT, "EX-001: snapshot mismatch")
    levels = data["primary_factor_levels"]
    _exact_keys(levels, {"semantic_ambiguity", "syntax_relation"}, "EX-001 factor levels")
    _require(levels["semantic_ambiguity"] == ["low", "high"], "EX-001: ambiguity levels drift")
    _require(levels["syntax_relation"] == ["parallel", "chiasmic_reversal"], "EX-001: syntax levels drift")
    conditions = data["factorial_conditions"]
    _require(isinstance(conditions, list) and len(conditions) == 4, "EX-001: factorial must contain four cells")
    _unique((row.get("id") for row in conditions), "EX-001 conditions")
    expected_pairs = {(a, b) for a in levels["semantic_ambiguity"] for b in levels["syntax_relation"]}
    observed_pairs: set[tuple[str, str]] = set()
    for row in conditions:
        _exact_keys(row, {"id", "factors"}, row.get("id", "EX-001 cell"))
        _exact_keys(row["factors"], set(levels), row["id"] + ".factors")
        pair = (row["factors"]["semantic_ambiguity"], row["factors"]["syntax_relation"])
        _require(pair in expected_pairs, f"{row['id']}: invalid factor value")
        observed_pairs.add(pair)
    _require(observed_pairs == expected_pairs, "EX-001: incomplete 2x2 factorial")
    controls = data["secondary_controls"]
    _require(isinstance(controls, list) and len(controls) == 3, "EX-001: control set mismatch")
    _unique((row.get("id") for row in controls), "EX-001 controls")
    for row in controls:
        _exact_keys(row, {"id", "control_type", "changed_fields", "purpose"}, row.get("id", "EX-001 control"))
        _require(isinstance(row["changed_fields"], list) and row["changed_fields"], f"{row['id']}: no changed fields")
    estimand = data["primary_estimand"]
    _exact_keys(estimand, {"id", "condition_refs", "formula", "direction", "smallest_effect", "null", "falsifier"}, "EX-001 estimand")
    condition_ids = {row["id"] for row in conditions}
    _require(set(estimand["condition_refs"]) == condition_ids, "EX-001: unresolved estimand condition ref")
    _require(data["primary_outcome"] == "blinded_count_of_distinct_coherent_interpretations", "EX-001: primary outcome drift")
    sampling = data["sampling"]
    _require(sampling["pilot_item_families_exact"] == 8 and sampling["pilot_model_runs_per_cell_exact"] == 2, "EX-001: pilot N drift")
    _require(sampling["confirmatory_locked"] is False and sampling["confirmatory_n"] is None, "EX-001: false preregistration")
    _require(set(data["null_register"]) == NULLS and len(data["null_register"]) == len(NULLS), "EX-001: null register mismatch")
    _require("attention_entropy_alone" in data["forbidden_primary_proxies"], "EX-001: attention guard missing")
    _require(set(data["run_manifest_fields"]) == RUN_FIELDS - {"protocol_id"}, "EX-001: run manifest field drift")


def validate_block_protocol(data: dict[str, Any]) -> None:
    required = {
        "schema_version", "protocol_id", "title", "status", "source_snapshot_commit", "objective",
        "non_claims", "seed_domains", "seed_exclusions", "global_fixed", "primary_outcomes",
        "manipulation_checks", "lanes", "oscillation_classification", "sampling", "run_manifest_fields",
        "run_dispositions", "null_register", "evaluation",
    }
    _exact_keys(data, required, "EX-002")
    _require(data["schema_version"] == "0.2" and data["protocol_id"] == "REV:EX-002", "EX-002: identity mismatch")
    _require(data["status"] == "pilot_design", "EX-002: status must be pilot_design")
    _require(data["source_snapshot_commit"] == SOURCE_COMMIT, "EX-002: snapshot mismatch")
    _require("wave_language" in data["seed_exclusions"], "EX-002: wave exclusion missing")
    outcomes = set(data["primary_outcomes"])
    required_outcomes = {"FRAME_SELECTED", "CONSTRAINTS_RETAINED", "SWITCH_AFTER_DISCRIMINATOR", "HELDOUT_ACCURACY", "TASK_SUCCESS", "CONFUSION"}
    _require(required_outcomes <= outcomes, "EX-002: primary outcomes incomplete")
    lanes = data["lanes"]
    _require(isinstance(lanes, list) and len(lanes) == 6, "EX-002: expected six separate lanes")
    _unique((lane.get("id") for lane in lanes), "EX-002 lanes")
    expected_lane_ids = {"REV:EX2:L-PRIME", "REV:EX2:L-COMMIT", "REV:EX2:L-BLOCK", "REV:EX2:L-ROLE", "REV:EX2:L-VARIANCE", "REV:EX2:L-RECIP"}
    _require({lane["id"] for lane in lanes} == expected_lane_ids, "EX-002: lane identity drift")
    all_arm_ids: list[str] = []
    for lane in lanes:
        _exact_keys(lane, {"id", "construct", "vary", "factor_keys", "arms", "estimand"}, lane.get("id", "EX-002 lane"))
        factor_keys = lane["factor_keys"]
        _require(isinstance(factor_keys, list) and factor_keys, f"{lane['id']}: factor keys missing")
        _require(len(factor_keys) == len(set(factor_keys)), f"{lane['id']}: duplicate factor key")
        _require(set(lane["vary"]) <= set(factor_keys), f"{lane['id']}: vary outside factor keys")
        arms = lane["arms"]
        _require(isinstance(arms, list) and len(arms) >= 4, f"{lane['id']}: insufficient arms")
        _unique((arm.get("id") for arm in arms), lane["id"] + " arms")
        for arm in arms:
            _exact_keys(arm, {"id", "factors"}, arm.get("id", "EX-002 arm"))
            _exact_keys(arm["factors"], set(factor_keys), arm["id"] + ".factors")
            for key, value in arm["factors"].items():
                _require(key in EX2_LEVELS and value in EX2_LEVELS[key], f"{arm['id']}: invalid {key}={value}")
            all_arm_ids.append(arm["id"])
        estimand = lane["estimand"]
        _exact_keys(estimand, {"outcome", "contrast", "null", "decision_rule"}, lane["id"] + ".estimand")
        _require(estimand["outcome"] in outcomes, f"{lane['id']}: unknown outcome ref")
    _unique(all_arm_ids, "EX-002 global arm ids")
    role_lane = next(lane for lane in lanes if lane["id"] == "REV:EX2:L-ROLE")
    role_pairs = {(arm["factors"]["role_frame"], arm["factors"]["response_policy"]) for arm in role_lane["arms"]}
    _require(role_pairs == {("helpful", "direct"), ("helpful", "branch"), ("peer", "direct"), ("peer", "branch")}, "EX-002: role-only contrasts missing")
    block_lane = next(lane for lane in lanes if lane["id"] == "REV:EX2:L-BLOCK")
    block_ids = {arm["id"] for arm in block_lane["arms"]}
    _require({"REV:EX2:BLOCK-UNREAD", "REV:EX2:BLOCK-INLINE", "REV:EX2:BLOCK-TOOL", "REV:EX2:BLOCK-PROSE"} <= block_ids, "EX-002: block comparators missing")
    sampling = data["sampling"]
    _require(sampling["pilot_runs_per_arm_exact"] == 2, "EX-002: pilot N drift")
    _require(sampling["confirmatory_locked"] is False and sampling["confirmatory_n"] is None, "EX-002: false preregistration")
    _require(sampling["all_launched_returned_refused_missing_and_selected_outputs_in_denominator"] is True, "EX-002: denominator not locked")
    _require(set(data["run_manifest_fields"]) == RUN_FIELDS - {"protocol_id"}, "EX-002: run manifest field drift")
    _require(set(data["null_register"]) == NULLS and len(data["null_register"]) == len(NULLS), "EX-002: null register mismatch")
    classification = data["oscillation_classification"]
    _require(len(classification["required"]) == 7, "EX-002: oscillation pass can be forged")
    _require("branching_only" in classification["alternative_exits"] and "joint_revision" in classification["alternative_exits"], "EX-002: alternative exits missing")


def validate_block_assets(schema: dict[str, Any], example: dict[str, Any]) -> None:
    _require(schema.get("additionalProperties") is False, "block schema: must reject unknown keys")
    required = set(schema.get("required", []))
    expected = {"schema_version", "block_id", "claim", "active_rivals", "nulls", "strongest_counterexample", "falsifier", "return_if", "compression_losses", "provenance", "decision"}
    _require(required == expected, "block schema: required fields drift")
    _exact_keys(example, expected, "block example")
    _require(example["schema_version"] == "0.2", "block example: version mismatch")
    _require(example["block_id"].startswith("REV:BLOCK:"), "block example: id not namespaced")
    rivals = example["active_rivals"]
    _require(isinstance(rivals, list) and rivals, "block example: no rival")
    _unique((rival.get("id") for rival in rivals), "block rivals")
    for rival in rivals:
        _exact_keys(rival, {"id", "prediction", "falsifier", "support", "state", "return_if"}, rival.get("id", "rival"))
    hashes = example["provenance"]["source_hashes"]
    _require(all(bool(SHA256_RE.fullmatch(value)) and value != "0" * 64 for value in hashes), "block example: placeholder source hash")


def validate_result_schema(schema: dict[str, Any]) -> None:
    _require(schema.get("additionalProperties") is False, "run schema: must reject unknown keys")
    required = set(schema.get("required", []))
    _require(required == RUN_FIELDS | {"schema_version"}, "run schema: required fields drift")
    denominator = schema.get("properties", {}).get("denominator_included", {})
    _require(denominator.get("const") is True, "run schema: denominator can be silently dropped")


def validate_pilot_protocol(data: dict[str, Any]) -> None:
    required = {"schema_version", "pilot_id", "protocol_ref", "lane_ref", "status", "objective", "design_limits", "arms", "common_constraints", "heldout_events", "response_fields", "locked_checks", "scoring", "denominator_rule", "created_before_collection"}
    _exact_keys(data, required, "PILOT-001")
    _require(data["schema_version"] == "0.2" and data["pilot_id"] == "REV:PILOT-001", "PILOT-001: identity mismatch")
    _require(data["protocol_ref"] == "REV:EX-002" and data["lane_ref"] == "REV:EX2:L-BLOCK", "PILOT-001: wrong parent")
    arms = data["arms"]
    _require(isinstance(arms, list) and len(arms) == 5, "PILOT-001: expected five arms")
    _unique((arm.get("id") for arm in arms), "PILOT-001 arms")
    for arm in arms:
        _exact_keys(arm, {"id", "runs_exact", "memory_condition"}, arm.get("id", "pilot arm"))
        _require(arm["runs_exact"] == 2, f"{arm['id']}: N drift")
    checks = data["locked_checks"]
    _require(isinstance(checks, list) and len(checks) == 6, "PILOT-001: locked checks drift")
    _unique((check.get("id") for check in checks), "PILOT-001 checks")
    _require("All ten launched runs" in data["denominator_rule"], "PILOT-001: denominator count missing")


def validate_pilot2(
    protocol: dict[str, Any],
    requests: dict[str, Any],
    outputs: dict[str, Any],
    assignment: dict[str, Any],
    judges: dict[str, Any],
    results: dict[str, Any],
) -> None:
    _exact_keys(
        protocol,
        {
            "schema_version", "pilot_id", "parent_lane", "status", "question", "arms",
            "runs_per_arm_exact", "total_runs_exact", "primary_comparison", "seed_facts",
            "heldout_event", "required_answer", "objective_score_keys", "non_claims",
        },
        "PILOT-002 protocol",
    )
    _require(protocol["schema_version"] == "0.1" and protocol["pilot_id"] == "REV:PILOT-002", "PILOT-002: identity mismatch")
    _require(protocol["status"] == "exploratory_fixed_denominator", "PILOT-002: status mismatch")
    arms = protocol["arms"]
    _require(set(arms) == {"structured", "prose", "shuffled", "absent"} and len(arms) == 4, "PILOT-002: arm set mismatch")
    _require(protocol["runs_per_arm_exact"] == 2 and protocol["total_runs_exact"] == 8, "PILOT-002: denominator drift")
    score_keys = protocol["objective_score_keys"]
    _require(isinstance(score_keys, list) and len(score_keys) == 8 and len(set(score_keys)) == 8, "PILOT-002: score-key drift")

    _exact_keys(requests, {"schema_version", "pilot_id", "common_suffix", "requests"}, "PILOT-002 requests")
    _require(requests["pilot_id"] == "REV:PILOT-002", "PILOT-002: request identity")
    request_rows = requests["requests"]
    _require(isinstance(request_rows, list) and len(request_rows) == 4, "PILOT-002: request count")
    _unique((row.get("request_id") for row in request_rows), "PILOT-002 request ids")
    _require({row.get("arm") for row in request_rows} == set(arms), "PILOT-002: request arm coverage")
    for row in request_rows:
        _exact_keys(row, {"arm", "request_id", "context"}, row.get("request_id", "PILOT-002 request"))
        _require(row["request_id"].startswith("REV:PILOT-002:REQ-"), f"{row['request_id']}: namespace")

    _exact_keys(outputs, {"schema_version", "pilot_id", "blinding", "outputs"}, "PILOT-002 blind outputs")
    output_rows = outputs["outputs"]
    _require(isinstance(output_rows, list) and len(output_rows) == 8, "PILOT-002: output denominator")
    _unique((row.get("label") for row in output_rows), "PILOT-002 output labels")
    labels = {row["label"] for row in output_rows}
    _require(labels == {f"R{index:02d}" for index in range(1, 9)}, "PILOT-002: output labels")
    for row in output_rows:
        _exact_keys(row, {"label", "completion"}, row["label"])
        _exact_keys(row["completion"], set(protocol["required_answer"]), row["label"] + ".completion")

    _exact_keys(assignment, {"schema_version", "pilot_id", "mapping"}, "PILOT-002 assignment")
    mapping = assignment["mapping"]
    _require(isinstance(mapping, list) and len(mapping) == 8, "PILOT-002: assignment denominator")
    _unique((row.get("label") for row in mapping), "PILOT-002 assignment labels")
    _unique((row.get("agent_id") for row in mapping), "PILOT-002 agent ids")
    _require({row["label"] for row in mapping} == labels, "PILOT-002: assignment label coverage")
    arm_counts = {arm: 0 for arm in arms}
    for row in mapping:
        _exact_keys(row, {"label", "arm", "agent_id"}, "PILOT-002 mapping")
        _require(row["arm"] in arm_counts, "PILOT-002: unknown assigned arm")
        arm_counts[row["arm"]] += 1
    _require(set(arm_counts.values()) == {2}, "PILOT-002: arm denominator")

    _exact_keys(judges, {"schema_version", "pilot_id", "scoring_rule", "scorers"}, "PILOT-002 judges")
    scorer_rows = judges["scorers"]
    _require(isinstance(scorer_rows, list) and len(scorer_rows) == 2, "PILOT-002: judge count")
    _unique((row.get("scorer") for row in scorer_rows), "PILOT-002 scorer ids")
    for scorer in scorer_rows:
        _exact_keys(scorer, {"scorer", "scores", "ambiguities"}, "PILOT-002 scorer")
        _require(len(scorer["scores"]) == 8, "PILOT-002: scorer denominator")
        _require({row["label"] for row in scorer["scores"]} == labels, "PILOT-002: scorer label coverage")
        for row in scorer["scores"]:
            _exact_keys(row, {"label", "items", "total", "one_line_reason"}, "PILOT-002 score row")
            _exact_keys(row["items"], set(score_keys), row["label"] + ".items")
            _require(all(value in (0, 1) and not isinstance(value, bool) for value in row["items"].values()), f"{row['label']}: nonbinary score")
            _require(row["total"] == sum(row["items"].values()), f"{row['label']}: scorer total")

    _exact_keys(results, {"schema_version", "pilot_id", "status", "runs", "arm_summary", "interpretation", "limitations"}, "PILOT-002 results")
    _require(results["status"] == "completed_exploratory", "PILOT-002: result status")
    _require("direct context-availability floor" in results["interpretation"], "PILOT-002: availability boundary missing")
    _require(any("not temporally interleaved" in item for item in results["limitations"]), "PILOT-002: batch confound missing")
    _require(any("request hashes" in item for item in results["limitations"]), "PILOT-002: runtime provenance limit missing")
    _require(isinstance(results["runs"], list) and len(results["runs"]) == 8, "PILOT-002: result denominator")
    _unique((row.get("run_id") for row in results["runs"]), "PILOT-002 run ids")
    result_labels = {row["label"] for row in results["runs"]}
    _require(result_labels == labels, "PILOT-002: result label coverage")
    output_by_label = {row["label"]: row["completion"] for row in output_rows}
    assignment_by_label = {row["label"]: row for row in mapping}
    score_by_scorer = [
        {row["label"]: row for row in scorer["scores"]}
        for scorer in scorer_rows
    ]
    for row in results["runs"]:
        _exact_keys(row, {"run_id", "label", "arm", "agent_id", "status", "output_hash", "scorer_totals", "consensus_scores", "score_total", "denominator_included"}, row.get("run_id", "PILOT-002 run"))
        _require(row["denominator_included"] is True, f"{row['run_id']}: denominator removal")
        _require(bool(SHA256_RE.fullmatch(row["output_hash"])), f"{row['run_id']}: output hash")
        canonical_output = json.dumps(output_by_label[row["label"]], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        _require(_sha256_bytes(canonical_output) == row["output_hash"], f"{row['run_id']}: output hash drift")
        assigned = assignment_by_label[row["label"]]
        _require(row["arm"] == assigned["arm"] and row["agent_id"] == assigned["agent_id"], f"{row['run_id']}: assignment drift")
        _exact_keys(row["consensus_scores"], set(score_keys), row["run_id"] + ".consensus")
        expected_totals = [scorer[row["label"]]["total"] for scorer in score_by_scorer]
        _require(row["scorer_totals"] == expected_totals, f"{row['run_id']}: scorer total drift")
        expected_consensus = {
            key: min(scorer[row["label"]]["items"][key] for scorer in score_by_scorer)
            for key in score_keys
        }
        _require(row["consensus_scores"] == expected_consensus, f"{row['run_id']}: consensus drift")
        _require(row["score_total"] == sum(row["consensus_scores"].values()), f"{row['run_id']}: consensus total")
        _require(isinstance(row["scorer_totals"], list) and len(row["scorer_totals"]) == 2, f"{row['run_id']}: scorer totals")
    _exact_keys(results["arm_summary"], set(arms), "PILOT-002 arm summary")
    for arm, summary in results["arm_summary"].items():
        _exact_keys(summary, {"n", "scores", "mean"}, f"PILOT-002 summary {arm}")
        observed = [row["score_total"] for row in results["runs"] if row["arm"] == arm]
        _require(summary["n"] == len(observed) == 2 and summary["scores"] == observed, f"PILOT-002: summary drift {arm}")
        _require(summary["mean"] == sum(observed) / len(observed), f"PILOT-002: mean drift {arm}")


def _git_bytes(commit: str, path: str) -> bytes:
    _require(bool(SHA40_RE.fullmatch(commit)), "Git: invalid commit syntax")
    exists = subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=REPO, capture_output=True)
    _require(exists.returncode == 0, f"Git: commit does not exist: {commit}")
    result = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=REPO, capture_output=True)
    _require(result.returncode == 0, f"Git: source path missing at snapshot: {path}")
    return result.stdout


def validate_manifest(data: dict[str, Any]) -> None:
    required = {"schema_version", "bundle_id", "source_snapshot_commit", "layer_state", "release_receipt", "restricted_sources", "source_artifacts", "layer_artifacts", "links"}
    _exact_keys(data, required, "bundle manifest")
    _require(data["schema_version"] == "0.3", "bundle manifest: version mismatch")
    _require(data["source_snapshot_commit"] == SOURCE_COMMIT, "bundle manifest: source snapshot mismatch")
    _require(data["layer_state"] == "public_release_approved", "bundle manifest: release approval missing")
    release = data["release_receipt"]
    _exact_keys(release, {"path", "approved_by", "approved_on", "scope", "raw_private_source"}, "release receipt")
    _require(release == {
        "path": "revolution/research/RELEASE_RECEIPT_2026-07-17.md",
        "approved_by": "den",
        "approved_on": "2026-07-17",
        "scope": "derived_research_results_and_agent_closeouts",
        "raw_private_source": "excluded",
    }, "bundle manifest: release scope drift")
    source_artifacts = data["source_artifacts"]
    _require(len(source_artifacts) == 5, "bundle manifest: expected Q-001..Q-005 source artifacts")
    for artifact in source_artifacts:
        _exact_keys(artifact, {"id", "path", "git_blob_oid", "sha256"}, artifact.get("id", "source artifact"))
        payload = _git_bytes(SOURCE_COMMIT, artifact["path"])
        oid = subprocess.run(["git", "rev-parse", f"{SOURCE_COMMIT}:{artifact['path']}"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
        _require(oid == artifact["git_blob_oid"], f"{artifact['id']}: Git blob mismatch")
        _require(_sha256_bytes(payload) == artifact["sha256"], f"{artifact['id']}: source SHA-256 mismatch")
    layer_artifacts = data["layer_artifacts"]
    _require(isinstance(layer_artifacts, list) and len(layer_artifacts) >= 12, "bundle manifest: layer artifact set too small")
    _unique((artifact.get("id") for artifact in layer_artifacts), "bundle layer artifacts")
    paths = set()
    for artifact in layer_artifacts:
        _exact_keys(artifact, {"id", "path", "sha256"}, artifact.get("id", "layer artifact"))
        path = REPO / artifact["path"]
        _require(path.is_file(), f"{artifact['id']}: layer file missing")
        _require(_sha256_path(path) == artifact["sha256"], f"{artifact['id']}: layer SHA-256 mismatch")
        paths.add(artifact["path"])
    for required_path in (
        "revolution/README.md",
        "revolution/Q-006_information_block_dynamics.md",
        "revolution/A-006_information_block_dynamics_v0_1.md",
        "revolution/research/RELEASE_RECEIPT_2026-07-17.md",
        "revolution/research/reviews/README.md",
        "revolution/research/reviews/2026-07-17_causal_statistical_review.md",
        "revolution/research/reviews/2026-07-17_multi_lens_synthesis.md",
        "revolution/research/reviews/2026-07-17_privacy_provenance_review.md",
        "revolution/research/EX-002_conversation_morphogenesis_protocol.json",
        "revolution/research/pilot/PILOT-001_block_reentry_protocol.json",
        "revolution/research/pilot/PILOT-002_block_rendering_protocol.json",
        "revolution/research/pilot/PILOT-002_results.json",
    ):
        _require(required_path in paths, f"bundle manifest: unregistered {required_path}")
    changed_result = subprocess.run(
        ["git", "diff", "--name-only", SOURCE_COMMIT, "--", "revolution"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    changed_paths = {line for line in changed_result.stdout.splitlines() if line}
    expected_paths = paths | {MANIFEST_PATH.relative_to(REPO).as_posix()}
    _require(changed_paths == expected_paths, "bundle manifest: whole-tree coverage mismatch")
    restricted = data["restricted_sources"]
    _require(len(restricted) == 1, "bundle manifest: restricted source count mismatch")
    receipt = restricted[0]
    _exact_keys(receipt, {"receipt_id", "research_agent_access", "public_abstracted_derivatives", "quoting", "path_disclosure"}, "restricted source")
    _require(receipt["research_agent_access"] is True, "restricted source: agent access missing")
    _require(receipt["public_abstracted_derivatives"] == "approved_public_release_2026-07-17", "restricted source: derived release approval missing")
    _require(receipt["quoting"] is False and receipt["path_disclosure"] is False, "restricted source: privacy boundary open")


def validate_cross_file_ids(*documents: dict[str, Any]) -> None:
    ids: list[str] = []
    ledger, text_protocol, block_protocol, pilot_protocol, pilot2_protocol, block_example = documents
    ids.extend(claim["id"] for claim in ledger["claims"])
    ids.append(text_protocol["protocol_id"])
    ids.extend(row["id"] for row in text_protocol["factorial_conditions"])
    ids.extend(row["id"] for row in text_protocol["secondary_controls"])
    ids.append(text_protocol["primary_estimand"]["id"])
    ids.append(block_protocol["protocol_id"])
    ids.extend(lane["id"] for lane in block_protocol["lanes"])
    ids.extend(arm["id"] for lane in block_protocol["lanes"] for arm in lane["arms"])
    ids.append(pilot_protocol["pilot_id"])
    ids.extend(arm["id"] for arm in pilot_protocol["arms"])
    ids.extend(check["id"] for check in pilot_protocol["locked_checks"])
    ids.append(pilot2_protocol["pilot_id"])
    ids.append(block_example["block_id"])
    ids.extend(rival["id"] for rival in block_example["active_rivals"])
    _unique(ids, "cross-file ids")


def main() -> int:
    try:
        ledger = load_json(LEDGER_PATH)
        text_protocol = load_json(TEXT_PROTOCOL_PATH)
        block_protocol = load_json(BLOCK_PROTOCOL_PATH)
        block_schema = load_json(BLOCK_SCHEMA_PATH)
        block_example = load_json(BLOCK_EXAMPLE_PATH)
        run_schema = load_json(RUN_SCHEMA_PATH)
        pilot_protocol = load_json(PILOT_PROTOCOL_PATH)
        pilot2_protocol = load_json(PILOT2_PROTOCOL_PATH)
        pilot2_requests = load_json(PILOT2_REQUESTS_PATH)
        pilot2_outputs = load_json(PILOT2_OUTPUTS_PATH)
        pilot2_assignment = load_json(PILOT2_ASSIGNMENT_PATH)
        pilot2_judges = load_json(PILOT2_JUDGES_PATH)
        pilot2_results = load_json(PILOT2_RESULTS_PATH)
        manifest = load_json(MANIFEST_PATH)
        validate_ledger(ledger)
        validate_text_protocol(text_protocol)
        validate_block_protocol(block_protocol)
        validate_block_assets(block_schema, block_example)
        validate_result_schema(run_schema)
        validate_pilot_protocol(pilot_protocol)
        validate_pilot2(
            pilot2_protocol,
            pilot2_requests,
            pilot2_outputs,
            pilot2_assignment,
            pilot2_judges,
            pilot2_results,
        )
        pilot_score = subprocess.run(
            [sys.executable, str(PILOT_SCORE_PATH)],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        _require(pilot_score.returncode == 0, f"PILOT-001 score receipt failed: {pilot_score.stderr.strip() or pilot_score.stdout.strip()}")
        validate_manifest(manifest)
        validate_cross_file_ids(
            ledger,
            text_protocol,
            block_protocol,
            pilot_protocol,
            pilot2_protocol,
            block_example,
        )
    except (OSError, json.JSONDecodeError, ValidationError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    pilot_runs = (
        len(load_json(PILOT_RESULTS_PATH).get("runs", []))
        + len(load_json(PILOT2_RESULTS_PATH).get("runs", []))
    )
    print(
        "OK: strict JSON; Git source snapshot verified; "
        f"{len(ledger['claims'])} bounded claim records; "
        "EX-001 2x2 pilot; EX-002 six matched lanes; "
        f"{pilot_runs} retained pilot runs; layer hashes exact"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

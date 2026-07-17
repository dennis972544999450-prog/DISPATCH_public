#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_research.py")
SPEC = importlib.util.spec_from_file_location("verify_research", MODULE_PATH)
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class ResearchVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = verify.load_json(verify.LEDGER_PATH)
        cls.text_protocol = verify.load_json(verify.TEXT_PROTOCOL_PATH)
        cls.block_protocol = verify.load_json(verify.BLOCK_PROTOCOL_PATH)
        cls.block_schema = verify.load_json(verify.BLOCK_SCHEMA_PATH)
        cls.block_example = verify.load_json(verify.BLOCK_EXAMPLE_PATH)
        cls.run_schema = verify.load_json(verify.RUN_SCHEMA_PATH)
        cls.pilot_protocol = verify.load_json(verify.PILOT_PROTOCOL_PATH)
        cls.pilot2_protocol = verify.load_json(verify.PILOT2_PROTOCOL_PATH)
        cls.pilot2_requests = verify.load_json(verify.PILOT2_REQUESTS_PATH)
        cls.pilot2_outputs = verify.load_json(verify.PILOT2_OUTPUTS_PATH)
        cls.pilot2_assignment = verify.load_json(verify.PILOT2_ASSIGNMENT_PATH)
        cls.pilot2_judges = verify.load_json(verify.PILOT2_JUDGES_PATH)
        cls.pilot2_results = verify.load_json(verify.PILOT2_RESULTS_PATH)
        cls.manifest = verify.load_json(verify.MANIFEST_PATH)

    def test_current_documents_validate_before_manifest(self) -> None:
        verify.validate_ledger(copy.deepcopy(self.ledger))
        verify.validate_text_protocol(copy.deepcopy(self.text_protocol))
        verify.validate_block_protocol(copy.deepcopy(self.block_protocol))
        verify.validate_result_schema(copy.deepcopy(self.run_schema))
        verify.validate_pilot_protocol(copy.deepcopy(self.pilot_protocol))

    def test_duplicate_json_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaisesRegex(verify.ValidationError, "duplicate key"):
                verify.load_json(path)

    def test_nan_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan.json"
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(verify.ValidationError, "non-finite"):
                verify.load_json(path)

    def test_unknown_ledger_key_fails(self) -> None:
        broken = copy.deepcopy(self.ledger)
        broken["claims"][0]["surprise"] = "silent schema drift"
        with self.assertRaisesRegex(verify.ValidationError, "unknown keys"):
            verify.validate_ledger(broken)

    def test_boolean_year_fails(self) -> None:
        broken = copy.deepcopy(self.ledger)
        broken["claims"][0]["source"]["year"] = True
        with self.assertRaisesRegex(verify.ValidationError, "invalid year"):
            verify.validate_ledger(broken)

    def test_t1_without_replication_schema_fails(self) -> None:
        broken = copy.deepcopy(self.ledger)
        broken["claims"][0]["strength"] = "rev:T1"
        with self.assertRaisesRegex(verify.ValidationError, "replication schema"):
            verify.validate_ledger(broken)

    def test_invalid_text_factor_value_fails(self) -> None:
        broken = copy.deepcopy(self.text_protocol)
        broken["factorial_conditions"][0]["factors"]["semantic_ambiguity"] = "banana"
        with self.assertRaisesRegex(verify.ValidationError, "invalid factor value"):
            verify.validate_text_protocol(broken)

    def test_unresolved_estimand_ref_fails(self) -> None:
        broken = copy.deepcopy(self.text_protocol)
        broken["primary_estimand"]["condition_refs"][0] = "REV:EX1:C-MISSING"
        with self.assertRaisesRegex(verify.ValidationError, "unresolved"):
            verify.validate_text_protocol(broken)

    def test_invalid_block_factor_value_fails(self) -> None:
        broken = copy.deepcopy(self.block_protocol)
        broken["lanes"][0]["arms"][0]["factors"]["prime_type"] = "banana"
        with self.assertRaisesRegex(verify.ValidationError, "invalid prime_type"):
            verify.validate_block_protocol(broken)

    def test_role_only_control_cannot_disappear(self) -> None:
        broken = copy.deepcopy(self.block_protocol)
        role_lane = next(lane for lane in broken["lanes"] if lane["id"] == "REV:EX2:L-ROLE")
        role_lane["arms"][3]["factors"] = copy.deepcopy(role_lane["arms"][2]["factors"])
        with self.assertRaisesRegex(verify.ValidationError, "role-only"):
            verify.validate_block_protocol(broken)

    def test_denominator_guard_fails_closed(self) -> None:
        broken = copy.deepcopy(self.block_protocol)
        broken["sampling"]["all_launched_returned_refused_missing_and_selected_outputs_in_denominator"] = False
        with self.assertRaisesRegex(verify.ValidationError, "denominator"):
            verify.validate_block_protocol(broken)

    def test_placeholder_block_hash_fails(self) -> None:
        broken = copy.deepcopy(self.block_example)
        broken["provenance"]["source_hashes"] = ["0" * 64]
        with self.assertRaisesRegex(verify.ValidationError, "placeholder"):
            verify.validate_block_assets(self.block_schema, broken)

    def test_nonexistent_git_commit_fails(self) -> None:
        with self.assertRaisesRegex(verify.ValidationError, "does not exist"):
            verify._git_bytes("0" * 40, "revolution/Q-001_wave_consciousness.md")

    def test_run_schema_requires_denominator_true(self) -> None:
        broken = copy.deepcopy(self.run_schema)
        broken["properties"]["denominator_included"] = {"type": "boolean"}
        with self.assertRaisesRegex(verify.ValidationError, "denominator"):
            verify.validate_result_schema(broken)

    def test_cross_file_collision_fails(self) -> None:
        broken_pilot = copy.deepcopy(self.pilot_protocol)
        broken_pilot["pilot_id"] = self.block_protocol["protocol_id"]
        with self.assertRaisesRegex(verify.ValidationError, "duplicate"):
            verify.validate_cross_file_ids(
                self.ledger,
                self.text_protocol,
                self.block_protocol,
                broken_pilot,
                self.pilot2_protocol,
                self.block_example,
            )

    def test_pilot2_current_files_validate(self) -> None:
        verify.validate_pilot2(
            copy.deepcopy(self.pilot2_protocol),
            copy.deepcopy(self.pilot2_requests),
            copy.deepcopy(self.pilot2_outputs),
            copy.deepcopy(self.pilot2_assignment),
            copy.deepcopy(self.pilot2_judges),
            copy.deepcopy(self.pilot2_results),
        )

    def test_pilot2_denominator_cannot_shrink(self) -> None:
        broken = copy.deepcopy(self.pilot2_results)
        broken["runs"].pop()
        with self.assertRaisesRegex(verify.ValidationError, "result denominator"):
            verify.validate_pilot2(
                self.pilot2_protocol,
                self.pilot2_requests,
                self.pilot2_outputs,
                self.pilot2_assignment,
                self.pilot2_judges,
                broken,
            )

    def test_pilot2_score_total_is_recomputed(self) -> None:
        broken = copy.deepcopy(self.pilot2_results)
        broken["runs"][0]["score_total"] = 7
        with self.assertRaisesRegex(verify.ValidationError, "consensus total"):
            verify.validate_pilot2(
                self.pilot2_protocol,
                self.pilot2_requests,
                self.pilot2_outputs,
                self.pilot2_assignment,
                self.pilot2_judges,
                broken,
            )

    def test_pilot2_batch_confound_cannot_disappear(self) -> None:
        broken = copy.deepcopy(self.pilot2_results)
        broken["limitations"] = [
            item for item in broken["limitations"]
            if "not temporally interleaved" not in item
        ]
        with self.assertRaisesRegex(verify.ValidationError, "batch confound"):
            verify.validate_pilot2(
                self.pilot2_protocol,
                self.pilot2_requests,
                self.pilot2_outputs,
                self.pilot2_assignment,
                self.pilot2_judges,
                broken,
            )

    def test_pilot2_runtime_provenance_limit_cannot_disappear(self) -> None:
        broken = copy.deepcopy(self.pilot2_results)
        broken["limitations"] = [
            item for item in broken["limitations"]
            if "request hashes" not in item
        ]
        with self.assertRaisesRegex(verify.ValidationError, "runtime provenance"):
            verify.validate_pilot2(
                self.pilot2_protocol,
                self.pilot2_requests,
                self.pilot2_outputs,
                self.pilot2_assignment,
                self.pilot2_judges,
                broken,
            )

    def test_manifest_covers_changed_revolution_tree(self) -> None:
        verify.validate_manifest(copy.deepcopy(self.manifest))

    def test_manifest_cannot_omit_changed_layer_file(self) -> None:
        broken = copy.deepcopy(self.manifest)
        broken["layer_artifacts"] = [
            item for item in broken["layer_artifacts"]
            if item["id"] != "REV:SOURCE-LEDGER"
        ]
        with self.assertRaisesRegex(verify.ValidationError, "whole-tree coverage"):
            verify.validate_manifest(broken)


if __name__ == "__main__":
    unittest.main()

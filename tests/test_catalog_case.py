import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("catalog_case", ROOT / "scripts/catalog-case.py")
case_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case_module)


class CatalogCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "case.json"
        self.assertEqual(case_module.main(["init", "--file", str(self.path), "--case-id", "case-1", "--workspace-id", "private-1"]), 0)

    def put(self, collection, record, revision=None):
        if revision is None:
            revision = case_module.read_case(self.path)["revision"]
        data = self.path.with_name("record.json")
        data.write_text(json.dumps(record))
        return case_module.main(["put", "--file", str(self.path), "--collection", collection, "--record", str(data), "--expected-revision", str(revision)])

    def source(self, rid="s1", version="v1"):
        return {"id": rid, "version": version, "sha256": "a" * 64, "status": "active", "locator": "private-original.csv", "evidence_kind": "provider_receipt"}

    def derived(self, rid="f1"):
        return {"id": rid, "stage": "audit", "status": "open", "rule_version": "test-v1", "cause_id": "cause-1", "source_refs": [{"source_id": "s1", "version": "v1"}], "summary": "private title and person"}

    def action(self):
        return {"id": "action-1", "stage": "register", "status": "prepared", "rule_version": "test-v1", "source_refs": [{"source_id": "s1", "version": "v1"}], "payload": {"provider": "example", "operation": "amend", "account": "account-private", "party": "party-1", "subjects": ["work-1"], "scope": {"territory": "US"}, "disclosure": ["split evidence"], "costs": []}}

    def test_resume_hosted_snapshot_without_local_history(self):
        self.put("sources", self.source())
        self.put("findings", self.derived())
        snapshot = case_module.read_case(self.path)
        del snapshot["history"]
        snapshot["revision"] = 7
        self.path.write_text(json.dumps(snapshot))
        self.assertEqual(self.put("sources", self.source(version="v2"), revision=7), 0)
        resumed = case_module.read_case(self.path)
        self.assertEqual(resumed["revision"], 8)
        self.assertEqual(len(resumed["history"]), 1)
        self.assertEqual(resumed["history"][0]["revision"], 7)
        self.assertEqual(resumed["history"][0]["records"]["sources"], snapshot["sources"])
        self.assertTrue(resumed["findings"]["f1"]["stale"])
        self.assertEqual(self.put("sources", self.source("s2"), revision=7), 2)

    def test_redacted_snapshot_cannot_be_resumed_for_writes(self):
        snapshot = case_module.read_case(self.path)
        del snapshot["history"]
        snapshot["sources"]["s1"] = {"id": "s1", "version": "v1", "status": "withdrawn", "withheld": True}
        self.path.write_text(json.dumps(snapshot))
        before = self.path.read_bytes()
        self.assertEqual(self.put("sources", self.source("s2"), revision=0), 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_idempotent_source_and_stale_writer(self):
        source = self.source()
        self.assertEqual(self.put("sources", source), 0)
        self.assertEqual(self.put("sources", source), 0)
        self.assertEqual(case_module.read_case(self.path)["revision"], 1)
        self.assertEqual(self.put("sources", self.source("s2"), revision=0), 2)
        self.assertNotIn("s2", case_module.read_case(self.path)["sources"])

    def test_changed_version_invalidates_only_dependents_and_preserves_history(self):
        self.put("sources", self.source())
        self.put("sources", self.source("s2"))
        self.put("findings", self.derived())
        independent = self.derived("f2")
        independent["source_refs"][0]["source_id"] = "s2"
        self.put("findings", independent)
        follow = self.derived("f3")
        follow["source_refs"] = independent["source_refs"]
        follow["depends_on"] = ["f1"]
        self.put("findings", follow)
        self.put("sources", self.source(version="v2"))
        case = case_module.read_case(self.path)
        self.assertTrue(case["findings"]["f1"]["stale"])
        self.assertTrue(case["findings"]["f3"]["stale"])
        self.assertNotIn("stale", case["findings"]["f2"])
        self.assertEqual(case["history"][-1]["records"]["sources"]["s1"]["version"], "v1")
        self.assertEqual(self.put("findings", self.derived()), 2)

    def test_same_version_changed_bytes_rejected(self):
        self.put("sources", self.source())
        updated = self.source()
        updated["sha256"] = "b" * 64
        self.assertEqual(self.put("sources", updated), 2)

    def test_withdrawal_invalidates_action_and_related_outcome(self):
        self.put("sources", self.source())
        self.put("actions", self.action())
        result = {"id": "o1", "action_id": "action-1", "dimension": "provider_decision", "status": "accepted", "rule_version": "test-v1", "source_refs": [{"source_id": "s1", "version": "v1"}]}
        self.assertEqual(self.put("outcomes", result), 0)
        case = case_module.read_case(self.path)
        self.assertEqual(case_module.main(["withdraw", "--file", str(self.path), "--source-id", "s1", "--expected-revision", str(case["revision"])]), 0)
        case = case_module.read_case(self.path)
        self.assertTrue(case["actions"]["action-1"]["stale"])
        self.assertTrue(case["outcomes"]["o1"]["stale"])
        self.assertEqual(case["outcomes"]["o1"]["status"], "accepted")

    def test_review_cannot_authorize_mutation_and_payload_change_invalidates_authority(self):
        self.put("sources", self.source())
        action = self.action()
        action["stage"] = "audit"
        self.assertEqual(self.put("actions", action), 2)
        action["stage"] = "register"
        action["status"] = "authorized"
        action["authorization"] = {"reference": "user-instruction-1", "scope": action["payload"]["scope"], "payload_sha256": case_module.fingerprint(action["payload"]), "valid_until": "2099-01-01T00:00:00Z"}
        self.assertEqual(self.put("actions", action), 0)
        action["payload"]["subjects"] = ["work-other"]
        self.assertEqual(self.put("actions", action), 2)

    def test_unknown_outcome_blocks_blind_retry_but_user_report_is_not_authority(self):
        self.put("sources", self.source())
        action = self.action()
        self.put("actions", action)
        attempt = {"id": "attempt-1", "action_id": "action-1", "payload_sha256": case_module.fingerprint(action["payload"]), "status": "unknown_outcome", "source_refs": [], "evidence_gap": "transport timed out", "rule_version": "test-v1"}
        self.assertEqual(self.put("attempts", attempt), 0)
        second = {**attempt, "id": "attempt-2", "status": "observed_sent", "source_refs": [{"source_id": "s1", "version": "v1"}]}
        self.assertEqual(self.put("attempts", second), 2)
        self.assertEqual(case_module.main(["preflight", "--file", str(self.path), "--action-id", "action-1"]), 2)
        attempt["status"] = "acknowledged"
        attempt["source_refs"] = second["source_refs"]
        self.assertEqual(self.put("attempts", attempt), 0)

    def test_export_excludes_originals_payloads_summaries_and_history(self):
        self.put("sources", self.source())
        self.put("findings", self.derived())
        self.put("actions", self.action())
        exported = case_module.summary(case_module.read_case(self.path))
        serialized = json.dumps(exported)
        for value in ("private-original", "private title", "account-private", "history", "payload", "locator"):
            self.assertNotIn(value, serialized)
        self.assertEqual(exported["counts"]["actions"], 1)

    def test_historical_version_cannot_be_reassigned(self):
        self.put("sources", self.source())
        newer = self.source(version="v2")
        newer["sha256"] = "b" * 64
        self.put("sources", newer)
        reused = self.source()
        reused["sha256"] = "c" * 64
        self.assertEqual(self.put("sources", reused), 2)

    def test_source_extensions_cannot_leak_nested_data_into_status_projection(self):
        source = self.source()
        source["stage"] = {"secret": "PRIVATE RAW CONTENT"}
        source["dimension"] = {"account": "PRIVATE RAW CONTENT"}
        self.put("sources", source)
        self.assertNotIn("PRIVATE RAW CONTENT", json.dumps(case_module.summary(case_module.read_case(self.path))))

    def test_unknown_outcome_cannot_be_downgraded_to_unblock_retry(self):
        self.put("sources", self.source())
        action = self.action()
        self.put("actions", action)
        attempt = {"id": "attempt-1", "action_id": "action-1", "payload_sha256": case_module.fingerprint(action["payload"]), "status": "unknown_outcome", "source_refs": [], "evidence_gap": "timeout", "rule_version": "test-v1"}
        self.put("attempts", attempt)
        attempt["status"] = "user_reported_sent"
        self.assertEqual(self.put("attempts", attempt), 2)

    def test_empty_payload_cannot_be_prepared_or_authorized(self):
        self.put("sources", self.source())
        for field in ("provider", "operation", "party", "account", "subjects", "scope"):
            action = self.action()
            action["payload"][field] = None
            self.assertEqual(self.put("actions", action), 2)

    def test_provider_receipt_cannot_prove_bank_receipt(self):
        self.put("sources", self.source())
        self.put("actions", self.action())
        result = {"id": "o1", "action_id": "action-1", "dimension": "financial_effect", "status": "bank_received", "rule_version": "test-v1", "source_refs": [{"source_id": "s1", "version": "v1"}]}
        self.assertEqual(self.put("outcomes", result), 2)
        bank = self.source("bank-1")
        bank["evidence_kind"] = "bank_receipt"
        self.put("sources", bank)
        result["source_refs"] = [{"source_id": "bank-1", "version": "v1"}]
        self.assertEqual(self.put("outcomes", result), 0)

    def test_observation_and_cash_are_separate_dimensions(self):
        self.put("sources", self.source())
        self.put("actions", self.action())
        result = {"id": "o1", "action_id": "action-1", "dimension": "provider_decision", "status": "bank_received", "rule_version": "test-v1", "source_refs": [{"source_id": "s1", "version": "v1"}]}
        self.assertEqual(self.put("outcomes", result), 2)


if __name__ == "__main__":
    unittest.main()

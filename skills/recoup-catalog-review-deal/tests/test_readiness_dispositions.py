"""CATD23: accepted/deferred exceptions must retain accountable scoped evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build-deal-readiness.py"
SPEC = importlib.util.spec_from_file_location("readiness_dispositions", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DispositionTests(unittest.TestCase):
    def test_incomplete_exception_cannot_remove_a_critical_blocker(self):
        for status in ("accepted", "deferred"):
            for field in ("disposition_actor", "disposition_scope", "disposition_reason"):
                for value in (None, "", " ", {}, []):
                    with self.subTest(status=status, field=field, value=value), tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        (root / "findings").mkdir()
                        finding = {"finding_id": "F1", "severity": "critical", "status": status,
                                   "disposition_actor": "synthetic-reviewer", "disposition_scope": "One supplied work, US, 2024",
                                   "disposition_reason": "Documented exception", "disposition_evidence_ids": ["E1"]}
                        if value is None:
                            del finding[field]
                        else:
                            finding[field] = value
                        (root / "findings/findings.json").write_text(json.dumps({"findings": [finding]}))
                        with self.assertRaises(ValueError):
                            MOD.render_dashboard(root)

    def test_complete_exceptions_and_unresolved_findings_remain_distinct(self):
        for status in ("accepted", "deferred"):
            finding = {"status": status, "disposition_actor": "synthetic-reviewer", "disposition_scope": "work-one",
                       "disposition_reason": "Documented exception", "disposition_evidence_ids": ["E1"]}
            self.assertFalse(MOD.is_open(finding))
        for status in ("open", "pending", "in_progress"):
            self.assertTrue(MOD.is_open({"status": status}))
        for status in ("resolved", "closed"):
            self.assertFalse(MOD.is_open({"status": status, "disposition_reason": "Evidence reviewed", "disposition_evidence_ids": ["E1"]}))

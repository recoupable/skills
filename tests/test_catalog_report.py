import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("report", Path(__file__).resolve().parents[1] / "scripts/build-catalog-report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class ReportTests(unittest.TestCase):
    def test_selected_projection_excludes_extensions_and_formula_cells(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            case = {"schema_version": 1, "case_id": "synthetic", "revision": 1,
                    **{group: {} for group in report.COLLECTIONS}}
            case["sources"] = {"s1": {"id": "s1", "status": "active", "locator": "PRIVATE", "stage": "PRIVATE", "evidence_gap": {"raw": "PRIVATE"}}}
            case["findings"] = {"f1": {"id": "=CMD()", "summary": "PRIVATE SUMMARY", "source_refs": [{"source_id": "s1", "version": "v1", "raw": "PRIVATE"}], "depends_on": [{"raw": "PRIVATE"}], "evidence_gap": "Missing statement"}}
            source = root / "case.json"
            source.write_text(json.dumps(case))
            report.build(source, root / "export")
            combined = "".join(p.read_text() for p in (root / "export").iterdir())
            self.assertNotIn("PRIVATE", combined)
            with (root / "export/findings.csv").open() as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["id"], "'=CMD()")
            self.assertEqual(json.loads(row["source_refs"]), [{"source_id": "s1", "version": "v1"}])
            self.assertEqual(row["evidence_gap"], "Missing statement")
            report.build(source, root / "private-export", include_summary=True)
            self.assertIn("PRIVATE SUMMARY", (root / "private-export/findings.csv").read_text())
            with self.assertRaises(ValueError):
                report.build(source, root / "export")

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location("intake", Path(__file__).parents[1] / "scripts/import_catalog.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.mapping = {"entities": {"recording": {"title": "Title", "isrc": "ISRC"}, "release": {"title": "Release", "upc": "UPC"}}, "membership": {"track": "Track"}}

    def run_csv(self, content, previous=None):
        path = self.root / "catalog.csv"
        path.write_text(content)
        return MOD.intake(path, self.mapping, previous=previous)

    def test_recording_reused_in_two_editions_and_unicode_ids(self):
        result = self.run_csv("Title,ISRC,Release,UPC,Track\nÉtoile,AA0000000001,Single,00123,1\nÉtoile,AA0000000001,Album,00456,3\n")
        self.assertEqual(result["controls"]["entity_candidates"], {"recording": 1, "release": 2})
        self.assertEqual(len(result["release_memberships"]), 2)
        self.assertEqual(result["rows"][0]["raw"]["UPC"], "00123")
        self.assertEqual(result["hosted_save"]["status"], "not_attempted")

    def test_all_rows_accounted_and_title_does_not_merge(self):
        result = self.run_csv("Title,ISRC,Release,UPC,Track\nTwin,,One,001,1\nTwin,,Two,002,1\n\nToo,Many,Fields,In,This,Row\n")
        self.assertEqual(result["controls"]["input_rows"], 4)
        self.assertEqual(result["controls"]["accounted_rows"], 4)
        self.assertEqual(result["controls"]["dispositions"], {"held": 3, "rejected": 1})
        self.assertNotEqual(result["rows"][0]["entity_ids"]["recording"], result["rows"][1]["entity_ids"]["recording"])
        self.assertEqual(result["rows"][-1]["raw_values"][-1], "Row")

    def test_identity_conflicts_hold_both_observations(self):
        result = self.run_csv("Title,ISRC,Release,UPC,Track\nTwin,AA0000000001,One,001,1\nDifferent,AA0000000001,One,001,1\n")
        self.assertEqual(result["controls"]["dispositions"], {"held": 2})

    def test_repeat_and_revision(self):
        content = "Title,ISRC,Release,UPC,Track\nTwin,AA0000000001,One,001,1\n"
        first = self.run_csv(content)
        repeat = self.run_csv(content, first)
        self.assertEqual(first["import_id"], repeat["import_id"])
        self.assertEqual(repeat["controls"]["dispositions"], {"unchanged": 1})
        revised = self.run_csv(content.replace("Twin", "Other"), first)
        self.assertEqual(revised["supersedes_import_id"], first["import_id"])
        self.assertNotEqual(revised["import_id"], first["import_id"])

    def test_cli_preserves_all_inputs_for_equivalent_output_paths(self):
        content = "Title,ISRC,Release,UPC,Track\nTwin,AA0000000001,One,001,1\n"
        previous_result = self.run_csv(content)
        source = self.root / "catalog.csv"
        mapping = self.root / "mapping.json"
        mapping.write_text(json.dumps(self.mapping))
        previous = self.root / "previous.json"
        previous.write_text(json.dumps(previous_result))
        originals = {path: path.read_bytes() for path in (source, mapping, previous)}
        for target in originals:
            symlink = self.root / (target.name + ".symlink")
            symlink.symlink_to(target)
            hardlink = self.root / (target.name + ".hardlink")
            hardlink.hardlink_to(target)
            for output in (target, self.root / "." / target.name, symlink, hardlink):
                with self.subTest(target=target.name, output=output.name):
                    run = subprocess.run([sys.executable, str(SPEC.origin), "--source", str(source), "--mapping", str(mapping),
                                          "--previous", str(previous), "--out", str(output)], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                    self.assertIn("cannot overwrite", run.stderr)
                    for path, original in originals.items():
                        self.assertEqual(path.read_bytes(), original)

    def test_cli_writes_distinct_output_without_changing_source(self):
        self.run_csv("Title,ISRC,Release,UPC,Track\nTwin,AA0000000001,One,001,1\n")
        source = self.root / "catalog.csv"
        original = source.read_bytes()
        mapping = self.root / "mapping.json"
        mapping.write_text(json.dumps(self.mapping))
        output = self.root / "intake.json"
        run = subprocess.run([sys.executable, str(SPEC.origin), "--source", str(source), "--mapping", str(mapping),
                              "--out", str(output)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(output.read_text())["controls"]["input_rows"], 1)
        self.assertEqual(source.read_bytes(), original)

    def test_parented_interests_not_summed(self):
        self.mapping = {"entities": {"composition": {"title": "Title", "iswc": "ISWC"}}, "interest": {"kind": "Kind", "value": "Share", "basis": "Basis", "scale": "Scale", "parent_reference": "Parent"}}
        result = self.run_csv("Title,ISWC,Kind,Share,Basis,Scale,Parent\nWork,T0000000001,collection,50,provider_claim,100,P1\nWork,T0000000001,collection,50,provider_claim,100,P2\n")
        self.assertEqual(len(result["entities"]), 1)
        self.assertEqual(len(result["interest_observations"]), 2)
        self.assertNotIn("total_share", result)

    def test_interest_outliers_are_held_without_rewriting_source_values(self):
        self.mapping = {"entities": {"composition": {"title": "Title", "iswc": "ISWC"}}, "interest": {"kind": "Kind", "value": "Share", "basis": "Basis", "scale": "Scale"}}
        for value, scale in (("181", "100"), ("-1", "100"), ("unknown", "100"), ("NaN", "100"), ("Infinity", "100"), ("50", "0"), ("50", "unknown"), ("50", "NaN")):
            with self.subTest(value=value, scale=scale):
                content = f"Title,ISWC,Kind,Share,Basis,Scale\nWork,T0000000001,statement_percentage,{value},provider_claim,{scale}\n"
                result = self.run_csv(content)
                self.assertEqual(result["controls"]["dispositions"], {"held": 1})
                self.assertEqual(result["interest_observations"][0]["fields"]["value"], value)
                self.assertEqual(result["interest_observations"][0]["fields"]["scale"], scale)
                self.assertEqual(result["rows"][0]["raw"]["Share"], value)
                self.assertEqual(self.run_csv(content, result)["controls"]["dispositions"], {"held": 1})

    def test_interest_bounds_use_supplied_scale_without_rescaling(self):
        self.mapping = {"entities": {"composition": {"title": "Title", "iswc": "ISWC"}}, "interest": {"kind": "Kind", "value": "Share", "basis": "Basis", "scale": "Scale"}}
        for value, scale in (("0", "100"), ("100", "100"), ("150", "200"), ("0.5", "1")):
            with self.subTest(value=value, scale=scale):
                result = self.run_csv(f"Title,ISWC,Kind,Share,Basis,Scale\nWork,T0000000001,collection,{value},provider_claim,{scale}\n")
                self.assertEqual(result["controls"]["dispositions"], {"proposed": 1})
                self.assertEqual(result["interest_observations"][0]["fields"]["value"], value)
                self.assertNotIn("total_share", result)

    def test_xlsx_sheet_and_numeric_identifier_guard(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest("openpyxl unavailable")
        path = self.root / "catalog.xlsx"
        book = openpyxl.Workbook()
        book.active.title = "Works"
        book.active.append(["Title", "ISRC", "Release", "UPC", "Track"])
        book.active.append(["Étoile", "AA0000000001", "One", 123, 1])
        book.create_sheet("Notes")
        book.save(path)
        with self.assertRaisesRegex(ValueError, "Choose --sheet"):
            MOD.intake(path, self.mapping)
        with self.assertRaisesRegex(ValueError, "Unknown sheet"):
            MOD.intake(path, self.mapping, "Missing")
        result = MOD.intake(path, self.mapping, "Works")
        self.assertEqual(result["rows"][0]["status"], "held")
        self.assertIn("numeric identifier", " ".join(result["rows"][0]["reasons"]))


if __name__ == "__main__":
    unittest.main()

"""Synthetic controls must prove an observed field, including explicit zero totals."""
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("normalizer_controls_subject", SCRIPTS / "normalize-royalty-statement.py")
normalizer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = normalizer
SPEC.loader.exec_module(normalizer)


class SourceControlTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.row = {"Track Title": "Synthetic Control", "ISRC": "USZZZ2400001",
                    "Period Start": "2024-01-01", "Period End": "2024-03-31",
                    "Currency": "USD", "Gross": "0", "Net": "0", "Deductions": "0",
                    "Rights Type": "master", "Income Type": "streaming"}

    def tearDown(self):
        self.temporary.cleanup()

    def normalize(self, controls, row=None):
        source = self.root / "source.csv"
        record = self.row if row is None else row
        with source.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(record))
            writer.writeheader()
            writer.writerow(record)
        controls_path = self.root / "controls.json"
        controls_path.write_text(json.dumps(controls))
        return normalizer.normalize("distributor", source, self.root / "ledger.csv", controls_path=controls_path)

    def controls(self, field="owner_net_amount", currency="USD", amount="0", refs=None):
        return {"evidence_refs": ["synthetic:statement-total"] if refs is None else refs,
                "totals": [{"currency": currency, "field": field, "amount": amount}]}

    def assert_control_rejected(self, result):
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["controls_status"], "mismatch")
        self.assertTrue(result["warnings"])

    def test_unknown_zero_control_field_is_not_observed_zero(self):
        result = self.normalize(self.controls(field="owner_net_amout"))
        self.assert_control_rejected(result)
        self.assertNotIn("owner_net_amout", {total["field"] for total in result["source_totals"]})

    def test_all_evidence_refs_must_be_nonempty_strings(self):
        for refs in ([], [""], ["  "], [None], [123], "synthetic:statement-total", ["synthetic:valid", ""]):
            with self.subTest(refs=refs):
                self.assert_control_rejected(self.normalize(self.controls(refs=refs)))

    def test_explicit_zero_controls_match_each_supported_field(self):
        for field in ("gross_amount", "owner_net_amount", "deductions"):
            with self.subTest(field=field):
                result = self.normalize(self.controls(field=field, amount=0))
                self.assertEqual(result["controls_status"], "matched")
                self.assertEqual(result["status"], "ok")

    def test_missing_amount_is_not_observed_zero(self):
        row = {**self.row, "Gross": ""}
        self.assert_control_rejected(self.normalize(self.controls(field="gross_amount"), row=row))

    def test_unobserved_currency_is_not_observed_zero(self):
        result = self.normalize(self.controls(currency="EUR"))
        self.assert_control_rejected(result)
        self.assertEqual({total["currency"] for total in result["source_totals"]}, {"USD"})

    def test_control_currency_must_be_explicit_uppercase_code(self):
        for currency in ("", "usd", "US", None, 123):
            with self.subTest(currency=currency):
                self.assert_control_rejected(self.normalize(self.controls(currency=currency)))

    def test_invalid_control_amounts_fail_without_false_match(self):
        for amount in (None, False, "NaN", "Infinity", "not a number", "0.0000000000000000001"):
            with self.subTest(amount=amount):
                self.assert_control_rejected(self.normalize(self.controls(amount=amount)))

    def test_malformed_control_documents_fail_without_false_match(self):
        for controls in (None, [], "controls", {}, {"evidence_refs": ["synthetic:total"], "totals": "bad"},
                         {"evidence_refs": ["synthetic:total"], "totals": [None]},
                         {"evidence_refs": ["synthetic:total"], "totals": [{}]}):
            with self.subTest(controls=controls):
                self.assert_control_rejected(self.normalize(controls))

    def test_signed_subcent_control_preserves_exact_total(self):
        result = self.normalize(self.controls(amount="-0.0049"), row={**self.row, "Net": "-0.0049"})
        self.assertEqual(result["controls_status"], "matched")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

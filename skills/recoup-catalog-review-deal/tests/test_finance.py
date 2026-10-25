"""Behavior regressions. Every source and identifier in these tests is synthetic."""
import copy
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


normalizer = module("normalize-royalty-statement")
entitlement = module("calculate-entitlements")
remittance = module("reconcile-remittances")
ledger_validator = module("validate-normalized-ledger")
manifest = module("build-file-manifest")
readiness = module("build-deal-readiness")
consistency = module("validate-workspace-consistency")
queue = module("build-manual-review-queue")


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "statement.csv"
        self.output = self.root / "ledger.csv"
        self.row = {"Track Title": "Totals Eclipse", "ISRC": "USZZZ2400001", "Period Start": "2024-01-01", "Period End": "2024-03-31",
                    "Currency": "USD", "Gross": ".0049", "Net": ".0049", "Rights Type": "publishing", "Income Type": "performance"}

    def tearDown(self):
        self.temporary.cleanup()

    def source_rows(self, rows):
        keys = list(dict.fromkeys(key for row in rows for key in row)) if rows else list(self.row)
        with self.source.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    def normalize(self, **kwargs):
        return normalizer.normalize("distributor", self.source, self.output, **kwargs)

    def read_ledger(self):
        with self.output.open() as stream:
            return list(csv.DictReader(stream))

    def test_subcent_precision_and_title_not_footer(self):
        self.source_rows([self.row, {**self.row, "Track Title": "Note: New Song", "Net": "(0.0001)"}])
        result = self.normalize()
        self.assertEqual(result["status"], "ok")
        self.assertEqual([r["owner_net_amount"] for r in self.read_ledger()], ["0.0049", "-0.0001"])
        net = next(t for t in result["source_totals"] if t["field"] == "owner_net_amount")
        self.assertEqual(net["amount"], "0.0048")
        self.assertEqual(result["controls_status"], "unavailable")

    def test_missing_net_currency_and_classification_held(self):
        for key in ("Net", "Currency", "Rights Type", "Income Type"):
            with self.subTest(key=key):
                row = dict(self.row); del row[key]
                self.source_rows([row])
                result = self.normalize()
                self.assertEqual(result["status"], "partial")
                self.assertEqual(self.read_ledger()[0]["row_status"], "held")
                self.assertEqual(ledger_validator.validate(self.output)["status"], "errors_found")

    def test_report_date_never_payment_and_explicit_map_wins(self):
        self.source_rows([{**self.row, "Currency": "USD", "Settlement Currency": "EUR", "Report Date": "2024-04-30", "Payment Date": "2024-05-02"}])
        mapping = self.root / "map.json"
        mapping.write_text(json.dumps({"Settlement Currency": "currency"}))
        self.normalize(column_map_path=mapping)
        row = self.read_ledger()[0]
        self.assertEqual(row["currency"], "EUR")
        self.assertEqual(row["payment_date"], "2024-05-02")
        self.assertEqual(row["report_date"], "2024-04-30")

    def test_duplicate_append_does_not_add_economic_lines(self):
        self.source_rows([self.row])
        self.normalize()
        result = self.normalize(append=True)
        self.assertEqual(result["row_conservation"]["duplicate_rows"], 1)
        self.assertEqual(len(self.read_ledger()), 1)

    def test_economic_duplicates_cannot_greenlight_an_undercounted_ledger(self):
        row = {**self.row, "Gross": "50", "Net": "50", "Transaction ID": "TX-1", "Account ID": "A-1", "Statement ID": "ST-1"}
        self.source_rows([row, row])
        controls = self.root / "controls.json"
        controls.write_text(json.dumps({"evidence_refs": ["synthetic:control"], "totals": [{"currency": "USD", "field": "owner_net_amount", "amount": "100"}]}))
        result = self.normalize(controls_path=controls)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["controls_status"], "matched")
        self.assertEqual(result["ledger_control_status"], "requires_duplicate_review")
        self.assertEqual(next(t["amount"] for t in result["source_totals"] if t["field"] == "owner_net_amount"), "100")
        self.assertEqual(next(t["amount"] for t in result["written_totals"] if t["field"] == "owner_net_amount"), "50")
        self.assertEqual(sum(Decimal(row["owner_net_amount"]) for row in self.read_ledger()), Decimal("50"))
        self.assertEqual(result["row_conservation"]["economic_duplicate_rows"], 1)

    def test_source_controls_and_footer_conservation(self):
        self.source_rows([{**self.row, "Row Type": "detail"}, {**self.row, "Row Type": "control", "Net": ".0049"},
                          {**self.row, "Row Type": "footer", "Net": ""}, {**self.row, "Row Type": "ignored", "Net": ""}])
        controls = self.root / "controls.json"
        controls.write_text(json.dumps({"evidence_refs": ["synthetic:control"], "totals": [{"currency": "USD", "field": "owner_net_amount", "amount": "0.0049"}]}))
        result = self.normalize(controls_path=controls)
        counts = result["row_conservation"]
        self.assertEqual(counts["source_rows"], sum(counts.get(k, 0) for k in ("detail", "held", "control", "footer", "ignored", "duplicate_rows")))
        self.assertEqual(result["controls_status"], "matched")
        controls.write_text(json.dumps({"evidence_refs": ["synthetic:control"], "totals": [{"currency": "USD", "field": "owner_net_amount", "amount": "1"}]}))
        self.assertEqual(self.normalize(controls_path=controls)["status"], "partial")

    def test_changed_mapping_append_requires_rebuild(self):
        self.source_rows([self.row])
        self.normalize()
        mapping = self.root / "map.json"; mapping.write_text(json.dumps({"Gross": "owner_net_amount"}))
        original = self.output.read_bytes()
        with self.assertRaisesRegex(ValueError, "different mapping"):
            self.normalize(append=True, column_map_path=mapping)
        self.assertEqual(self.output.read_bytes(), original)

    def test_reimport_of_held_rows_remains_partial(self):
        self.source_rows([{**self.row, "Net": ""}])
        self.normalize()
        result = self.normalize(append=True)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(self.read_ledger()), 1)

    def test_explicit_transaction_revision_is_held(self):
        source = {**self.row, "Account ID": "ACCOUNT-A", "Statement ID": "Q1", "Transaction ID": "TX-1"}
        self.source_rows([source]); self.normalize()
        self.source_rows([{**source, "Net": "0.0031"}])
        result = self.normalize(append=True)
        self.assertEqual(result["status"], "partial")
        self.assertIn("revised_transaction", self.read_ledger()[-1]["held_reasons"])

    def test_invalid_gross_never_disappears_as_zero(self):
        self.source_rows([{**self.row, "Gross": "not a number"}])
        self.assertEqual(self.normalize()["status"], "partial")

    def test_header_only_not_success(self):
        self.source_rows([])
        self.assertEqual(self.normalize()["status"], "partial")
        self.assertEqual(ledger_validator.validate(self.output)["status"], "errors_found")

    def test_unknown_sheet_fails_without_output(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest("Install openpyxl for XLSX conformance")
        workbook = openpyxl.Workbook()
        workbook.active.append(list(self.row))
        workbook.active.append(list(self.row.values()))
        source = self.root / "statement.xlsx"
        workbook.save(source)
        with self.assertRaisesRegex(ValueError, "Requested worksheet"):
            normalizer.normalize("distributor", source, self.output, sheet="Missing")
        self.assertFalse(self.output.exists())

    def test_provider_does_not_overwrite_source_income(self):
        self.source_rows([{**self.row, "Rights Type": "master", "Income Type": "sync"}])
        normalizer.normalize("publisher-admin", self.source, self.output)
        self.assertEqual((self.read_ledger()[0]["rights_type"], self.read_ledger()[0]["income_type"]), ("master", "sync"))

    def test_manifest_needs_exact_parser_receipt(self):
        source_dir = self.root / "source"; source_dir.mkdir()
        target = source_dir / "statement.csv"; target.write_text("Title,Net\nA,1\n")
        initial = manifest.build_manifest(source_dir)
        self.assertEqual(initial[0]["parse_status"], "unparsed")
        receipt = {"source_version_id": initial[0]["sha256"], "input": str(target.resolve()), "parser_version": "2", "transform_id": "mapping", "rows": 1, "status": "ok", "receipt": "receipt.json"}
        self.assertEqual(manifest.build_manifest(source_dir, [receipt])[0]["parse_status"], "parsed")
        receipt["input"] = "/elsewhere/statement.csv"
        self.assertEqual(manifest.build_manifest(source_dir, [receipt])[0]["parse_status"], "unparsed")
        self.assertFalse(queue.file_contributed({"path": "source/B/statement.csv", "filename": "statement.csv"}, {"source/A/statement.csv"}))
        entry = {"path": "source/statement.csv", "sha256": "new-version"}
        self.assertFalse(queue.file_contributed(entry, {"source/statement.csv|sha256:old-version"}))
        self.assertTrue(queue.file_contributed(entry, {"source/statement.csv|sha256:new-version"}))

    def test_mixed_currency_and_period_are_separate_groups(self):
        self.source_rows([self.row, {**self.row, "Currency": "EUR"}, {**self.row, "Period Start": "2025-01-01", "Period End": "2025-03-31"}])
        self.normalize()
        run = subprocess.run([sys.executable, str(SCRIPTS / "calculate-concentration.py"), str(self.output)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertIsNone(result["total"])
        self.assertEqual(len(result["groups"]), 3)


class EntitlementTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "fixtures/finance/entitlement-input.json").read_text())

    def test_exact_entitlement_and_recoupment_bridge(self):
        result = entitlement.calculate(self.data)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["lines"][0]["expected_amount"], Decimal("40.002205"))
        self.assertEqual(result["recoupment_accounts"][0]["potential_payable"], Decimal("5.002205"))
        self.assertIsNone(result["lines"][0]["recovered_cash"])

    def test_missing_base_schedule_and_master_scope_block(self):
        for key, value in (("basis", None), ("adjustments_complete", False), ("rights_type", "master")):
            with self.subTest(key=key):
                data = copy.deepcopy(self.data); data["rules"][0][key] = value
                result = entitlement.calculate(data)
                self.assertEqual(result["status"], "partial")
                self.assertFalse(result["lines"])

    def test_double_commission_and_unsupported_terms_block(self):
        for change in ({"already_net_of": ["commission"]}, {"unsupported_terms": ["tiered escalator"]}):
            data = copy.deepcopy(self.data); data["rules"][0].update(change)
            self.assertFalse(entitlement.calculate(data)["lines"])

    def test_effective_change_cannot_span_rule(self):
        self.data["rules"][0]["effective_end"] = "2024-02-01"
        self.assertFalse(entitlement.calculate(self.data)["lines"])

    def test_negative_correction_and_overpayment(self):
        self.data["lines"][0].update({"gross_amount": "-100", "reported_amount": "0", "adjustments": []})
        result = entitlement.calculate(self.data)
        self.assertEqual(result["lines"][0]["expected_amount"], Decimal("-45.00"))
        self.assertEqual(result["lines"][0]["variance_direction"], "potential_overpayment_or_clawback")
        self.assertEqual(result["recoupment_accounts"][0]["closing_balance"], Decimal("80.00"))

    def test_duplicate_account_id_rejected(self):
        self.data["recoupment_accounts"].append(copy.deepcopy(self.data["recoupment_accounts"][0]))
        with self.assertRaisesRegex(ValueError, "account_id"):
            entitlement.calculate(self.data)

    def test_duplicate_adjustment_id_blocks_line(self):
        self.data["lines"][0]["adjustments"].append(copy.deepcopy(self.data["lines"][0]["adjustments"][0]))
        self.assertFalse(entitlement.calculate(self.data)["lines"])

    def test_arithmetic_limits_reject_overwide_and_preserve_max_supported(self):
        from _finance import amount
        for value in ("1000000000000000000000000", "0.0000000000000000001", "NaN"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                amount(value)
        base, rate = "999999.999999999999999999", "0.999999999999999999"
        self.data["lines"][0].update({"gross_amount": base, "reported_amount": "0", "adjustments": []})
        self.data["rules"][0].update({"participation_rate": rate, "commission_rate": rate})
        with localcontext() as context:
            context.prec = 256
            expected = Decimal(base) * Decimal(rate) * (1 - Decimal(rate))
        self.assertEqual(entitlement.calculate(self.data)["lines"][0]["expected_amount"], expected)

    def test_recoupment_overlap_blocked(self):
        self.data["recoupment_accounts"].append({**self.data["recoupment_accounts"][0], "account_id": "RECOUP-B"})
        result = entitlement.calculate(self.data)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["recoupment_accounts"]), 1)


class RemittanceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "fixtures/finance/remittance-input.json").read_text())

    def test_paid_is_not_received_and_unknown_is_not_zero(self):
        self.data["receipts"] = []; self.data["allocations"] = self.data["allocations"][:1]
        result = remittance.reconcile(self.data)
        self.assertEqual(result["verified_receipts_by_currency"], {})
        self.assertIsNone(result["current_payable"])

    def test_evidenced_fee_receipt(self):
        result = remittance.reconcile(self.data)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["verified_receipts_by_currency"], {"USD": Decimal("97")})

    def test_overallocation_and_duplicate_export_cannot_inflate(self):
        self.data["allocations"].append({**self.data["allocations"][1], "allocation_id": "DUP"})
        result = remittance.reconcile(self.data)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["verified_receipts_by_currency"], {"USD": Decimal("97")})
        self.data["receipts"].append(copy.deepcopy(self.data["receipts"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            remittance.reconcile(self.data)

    def test_user_reported_and_changed_account_not_verified(self):
        self.data["receipts"][0]["evidence_status"] = "user_reported"
        self.assertEqual(remittance.reconcile(self.data)["verified_receipts_by_currency"], {})
        self.data["receipts"][0]["account_ref"] = "HISTORICAL-ACCOUNT"
        self.assertEqual(remittance.reconcile(self.data)["status"], "partial")

    def test_renamed_duplicate_export_is_rejected(self):
        self.data["receipts"].append({**self.data["receipts"][0], "id": "DIFFERENT-LOCAL-ID"})
        with self.assertRaisesRegex(ValueError, "source_record_id"):
            remittance.reconcile(self.data)

    def test_partial_work_cannot_claim_complete(self):
        self.data["receipts"][0]["evidence_status"] = "user_reported"
        result = remittance.reconcile(self.data)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["unverified_allocation_ids"], ["ALLOC-B"])
        self.data["receipts"] = []; self.data["allocations"] = self.data["allocations"][:1]
        result = remittance.reconcile(self.data)
        self.assertEqual(result["status"], "partial")
        self.assertIn("remittance_to_receipt", result["missing_required_stages"])
        self.data["completion_scope"] = ["statement_to_remittance"]
        self.assertEqual(remittance.reconcile(self.data)["status"], "ok")

    def test_nonzero_residual_is_partial(self):
        self.data["statements"][0]["amount"] = "120"
        self.assertEqual(remittance.reconcile(self.data)["status"], "partial")

    def test_invalid_cli_input_is_structured_and_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source.json", Path(directory) / "output.json"
            source.write_text("[]")
            for filename in ("calculate-entitlements.py", "reconcile-remittances.py"):
                run = subprocess.run([sys.executable, str(SCRIPTS / filename), "--input", str(source), "--output", str(output)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(json.loads(run.stdout)["status"], "invalid_input")
                self.assertNotIn("Traceback", run.stderr)
                run = subprocess.run([sys.executable, str(SCRIPTS / filename), "--input", str(source), "--output", str(source)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(source.read_text(), "[]")

    def test_cli_output_aliases_preserve_original_evidence(self):
        for filename, fixture in (("calculate-entitlements.py", "entitlement-input.json"), ("reconcile-remittances.py", "remittance-input.json")):
            for link_kind in ("hardlink", "symlink"):
                for valid in (True, False):
                    with self.subTest(script=filename, link=link_kind, valid=valid), tempfile.TemporaryDirectory() as directory:
                        source, output = Path(directory) / "source.json", Path(directory) / "output.json"
                        original = (ROOT / "fixtures/finance" / fixture).read_bytes() if valid else b"[]"
                        source.write_bytes(original)
                        if link_kind == "hardlink":
                            output.hardlink_to(source)
                        else:
                            output.symlink_to(source)
                        run = subprocess.run([sys.executable, str(SCRIPTS / filename), "--input", str(source), "--output", str(output)], capture_output=True, text=True)
                        self.assertEqual(source.read_bytes(), original)
                        self.assertEqual(output.read_bytes(), original)
                        self.assertEqual(run.returncode, 1)
                        self.assertIn("overwrite source", json.loads(run.stdout)["errors"][0])
                        self.assertNotIn("Traceback", run.stderr)

    def test_grouped_and_split_receipts(self):
        self.data["receipts"][0]["amount"] = "40"
        self.data["receipts"].append({**self.data["receipts"][0], "id": "BANK-B", "source_record_id": "synthetic:BANK-B", "amount": "60"})
        self.data["allocations"][1].update({"from_amount": "40", "to_amount": "40", "adjustments": []})
        self.data["allocations"].append({**self.data["allocations"][1], "allocation_id": "ALLOC-C", "to_id": "BANK-B", "from_amount": "60", "to_amount": "60"})
        self.assertEqual(remittance.reconcile(self.data)["verified_receipts_by_currency"]["USD"], Decimal("100"))

    def test_explicit_fx_and_negative_return(self):
        self.data["receipts"][0].update({"currency": "EUR", "amount": "90"})
        self.data["allocations"][1].update({"to_amount": "90", "fx_rate": "0.9", "fx_evidence_refs": ["synthetic-fx:row-1"], "adjustments": []})
        self.assertEqual(remittance.reconcile(self.data)["verified_receipts_by_currency"], {"EUR": Decimal("90")})
        for collection in ("statements", "remittances", "receipts"):
            self.data[collection][0]["amount"] = "-" + self.data[collection][0]["amount"]
        for allocation in self.data["allocations"]:
            for key in ("from_amount", "to_amount"):
                allocation[key] = "-" + allocation[key]
        result = remittance.reconcile(self.data)
        self.assertEqual(result["verified_receipts_by_currency"]["EUR"], Decimal("-90"))
        self.assertEqual(result["allocations"][1]["status"], "verified_return")

    def test_fx_bridge_requires_nonempty_evidence_reference_list(self):
        self.data["receipts"][0].update({"currency": "EUR", "amount": "90"})
        self.data["allocations"][1].update({"to_amount": "90", "fx_rate": "0.9", "adjustments": []})
        for invalid in (None, [], [""], ["   "], "synthetic-fx:row-1", [1]):
            with self.subTest(evidence=invalid):
                self.data["allocations"][1]["fx_evidence_refs"] = invalid
                result = remittance.reconcile(self.data)
                self.assertEqual(result["status"], "partial")
                self.assertEqual(result["verified_receipts_by_currency"], {})
                self.assertIn("requires evidence_refs", result["unresolved"][0]["reason"])


class ReadinessTests(unittest.TestCase):
    def test_unknown_status_and_unsupported_acceptance_fail(self):
        with self.assertRaises(ValueError):
            readiness.is_open({"status": "resovled", "finding_id": "F1"})
        with self.assertRaises(ValueError):
            readiness.is_open({"status": "accepted", "finding_id": "F1"})
        self.assertTrue(readiness.is_open({"status": "pending"}))
        self.assertFalse(readiness.is_open({"status": "accepted", "disposition_reason": "disclosed", "disposition_evidence_ids": ["E1"]}))

    def test_transaction_exclusion_does_not_erase_owned_interest(self):
        catalog = [{"catalog_asset_id": "WORK-1", "title": "Example Work", "controlled_share": "50", "deal_eligibility": "excluded"}]
        self.assertEqual(consistency.validate_excluded_assets(["Example Work"], catalog)[0], [])
        rights = [{"catalog_asset_id": "WORK-1", "support_level": "missing", "notes": "Need termination clause exhibit; no evidence rights ended"}]
        self.assertEqual(consistency.validate_reverted_rights(rights, catalog), [])
        catalog[0]["deal_eligibility"] = "included"
        self.assertEqual(len(consistency.validate_excluded_assets(["Example Work"], catalog)[0]), 1)


if __name__ == "__main__":
    unittest.main()

"""Synthetic entitlement workpaper export: exact amounts, private projection, provenance."""
import copy
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/recoup-catalog-review-deal/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('royalty_export', SCRIPTS / 'build-royalty-workpaper.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class WorkpaperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = json.loads((SCRIPTS.parent / 'fixtures/finance/entitlement-input.json').read_text())
        self.source, self.result = self.root / 'input.json', self.root / 'result.json'
        self.output = self.root / 'export'

    def prepare(self):
        self.source.write_text(json.dumps(self.data))
        self.result.write_text(export.dumps(export.calculator().calculate(self.data)))

    def build(self, inventory=None):
        self.prepare()
        inventory_path = None
        if inventory is not None:
            inventory_path = self.root / 'inventory.json'
            inventory_path.write_text(json.dumps(inventory))
        before = [p.read_bytes() for p in [self.source, self.result]]
        manifest = export.build(self.source, self.result, self.output, '2026-11-18', inventory_path)
        self.assertEqual(before, [p.read_bytes() for p in [self.source, self.result]])
        payload = json.loads((self.output / 'workpaper.json').read_text())
        expected_files = {'entitlement-lines.csv', 'calculation-bridge.csv',
                          'recoupment-accounts.csv', 'unresolved.csv', 'evidence.csv',
                          'workpaper.json', 'report.md'}
        self.assertEqual({item['file'] for item in manifest['files']}, expected_files)
        self.assertEqual(len(manifest['files']), len(expected_files))
        self.assertEqual({p.name for p in self.output.iterdir()}, expected_files | {'manifest.json'})
        for item in manifest['files']:
            self.assertEqual(item['sha256'], hashlib.sha256((self.output / item['file']).read_bytes()).hexdigest())
        return payload

    def test_exact_arithmetic_period_sources_and_nonadditive_controls(self):
        payload = self.build()
        line = payload['schedules']['entitlement-lines'][0]
        self.assertEqual(line['expected_amount'], '40.002205')
        self.assertEqual(line['variance'], '0.002205')
        self.assertEqual(line['currency'], 'USD')
        self.assertEqual((line['period_start'], line['period_end']), ('2024-01-01', '2024-03-31'))
        self.assertEqual(line['basis'], 'gross_amount')
        self.assertEqual(line['freshness'], 'unknown')
        account = payload['schedules']['recoupment-accounts'][0]
        self.assertEqual(account['potential_payable'], '5.002205')
        self.assertEqual(account['earnings_line_refs'], [line['line_ref']])
        self.assertEqual(account['earnings_periods'], [['2024-01-01', '2024-03-31']])
        self.assertEqual(account['balance_as_of'], 'unknown_not_supplied_by_calculator')
        self.assertIsNone(line['recovered_cash'])
        self.assertIsNone(account['cash_received'])
        self.assertEqual(payload['controls']['recovery_rollup'], 'not_calculated')
        self.assertEqual(payload['controls']['source_control'], 'not_verified_by_exporter')
        self.assertEqual(payload['controls']['input_sha256'], hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_negative_csv_is_display_only_and_json_stays_exact(self):
        self.data['lines'][0]['reported_amount'] = '50'
        payload = self.build()
        self.assertEqual(payload['schedules']['entitlement-lines'][0]['variance'], '-9.997795')
        with (self.output / 'entitlement-lines.csv').open() as stream:
            self.assertEqual(next(csv.DictReader(stream))['variance'], "'-9.997795")
        for value in ['=CMD()', ' +CMD()', '@SUM(1)', '\t=CMD()', '-1']:
            self.assertTrue(export.cell(value).startswith("'"))

    def test_no_private_ids_free_text_extensions_or_account_details(self):
        self.data['lines'][0]['line_id'] = '=PRIVATE_ID()'
        self.data['recoupment_accounts'][0]['earnings_line_ids'] = ['=PRIVATE_ID()']
        self.data['rules'][0]['rule_version'] = 'PRIVATE_VERSION'
        self.data['rules'][0]['evidence_refs'] = ['https://PRIVATE/token=SECRET']
        self.data['lines'][0]['account_number'] = 'PRIVATE_ACCOUNT'
        self.data['raw'] = 'PRIVATE_RAW'
        self.build()
        combined = ''.join(p.read_text() for p in self.output.iterdir())
        self.assertNotIn('PRIVATE', combined)
        self.assertNotIn('SECRET', combined)
        self.assertIn(export.alias('line', '=PRIVATE_ID()'), combined)

    def inventory(self):
        refs = ['synthetic-contract:section-4', 'synthetic-statement:row-2',
                'synthetic-contract:section-5', 'synthetic-reserve:row-1',
                'synthetic-recoupment:page-1', 'synthetic-approved-cost:row-1']
        return {'schema_version': '1', 'sources': [{'evidence_ref': ref, 'source_sha256': 'a'*64,
                'current_sha256': 'a'*64, 'checked_on': '2026-11-18'} for ref in refs]}

    def test_current_supplied_versions_are_not_source_verification(self):
        payload = self.build(self.inventory())
        self.assertEqual(payload['controls']['freshness'], 'current_as_supplied')
        self.assertEqual(payload['controls']['source_control'], 'not_verified_by_exporter')

    def test_changed_source_is_stale_without_changing_amounts(self):
        inventory = self.inventory()
        inventory['sources'][1]['current_sha256'] = 'b'*64
        payload = self.build(inventory)
        self.assertEqual(payload['controls']['freshness'], 'stale')
        self.assertEqual(payload['schedules']['entitlement-lines'][0]['freshness'], 'stale')
        self.assertEqual(payload['schedules']['entitlement-lines'][0]['expected_amount'], '40.002205')

    def test_old_check_and_missing_version_remain_unknown(self):
        inventory = self.inventory()
        inventory['sources'][0]['checked_on'] = '2026-11-17'
        inventory['sources'][1]['current_sha256'] = None
        self.assertEqual(self.build(inventory)['controls']['freshness'], 'unknown')

    def test_future_check_refused_before_output(self):
        inventory = self.inventory()
        inventory['sources'][0]['checked_on'] = '2026-11-19'
        with self.assertRaisesRegex(ValueError, 'after report'):
            self.build(inventory)
        self.assertFalse(self.output.exists())

    def test_unknown_line_not_zero_and_private_blocker_not_exported(self):
        self.data['rules'][0]['unsupported_terms'] = 'PRIVATE_CLAUSE'
        payload = self.build()
        self.assertEqual(payload['controls']['result_status'], 'partial')
        self.assertEqual(payload['schedules']['entitlement-lines'], [])
        self.assertTrue(payload['schedules']['unresolved'])
        self.assertIsNone(payload['schedules']['unresolved'][0]['amount'])
        self.assertNotIn('PRIVATE_CLAUSE', ''.join(p.read_text() for p in self.output.iterdir()))

    def test_no_mixed_currency_or_shared_cause_recovery_sum(self):
        second = copy.deepcopy(self.data['lines'][0])
        second.update(line_id='SECOND', currency='EUR', cause_id='shared')
        self.data['lines'][0]['cause_id'] = 'shared'
        self.data['lines'].append(second)
        payload = self.build()
        self.assertEqual([r['currency'] for r in payload['schedules']['entitlement-lines']], ['USD', 'EUR'])
        self.assertEqual(payload['controls']['recovery_rollup'], 'not_calculated')
        self.assertIsNone(payload['controls']['recovered_cash'])

    def test_tampered_result_rejected_before_output(self):
        self.prepare()
        data = json.loads(self.result.read_text())
        data['lines'][0]['expected_amount'] = '1000000'
        self.result.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'differs'):
            export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())

    def test_duplicate_lines_rejected_by_existing_validator(self):
        self.data['lines'].append(copy.deepcopy(self.data['lines'][0]))
        self.source.write_text(json.dumps(self.data))
        self.result.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())

    def test_source_and_existing_output_aliases_not_overwritten(self):
        self.prepare()
        for target in [self.source, self.result, self.root]:
            with self.assertRaisesRegex(ValueError, 'already exists'):
                export.build(self.source, self.result, target, '2026-11-18')
        linked = self.root / 'alias'
        linked.symlink_to(self.source)
        before = self.source.read_bytes()
        with self.assertRaises(ValueError):
            export.build(self.source, self.result, linked, '2026-11-18')
        self.assertEqual(self.source.read_bytes(), before)

    def test_vendored_portable_cli_works(self):
        self.prepare()
        script = ROOT / 'skills/recoup-catalog-reconcile-royalties/scripts/build-royalty-workpaper.py'
        result = subprocess.run([sys.executable, str(script), '--input', str(self.source), '--result',
                                 str(self.result), '--as-of', '2026-11-18', '--output-directory', str(self.output)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.output / 'report.md').is_file())

    def test_numeric_hashes_are_rejected_before_output(self):
        for key in ('source_sha256', 'current_sha256'):
            with self.subTest(key=key):
                self.output = self.root / key
                inventory = self.inventory()
                inventory['sources'][0][key] = int('1' * 64)
                with self.assertRaisesRegex(ValueError, 'SHA256'):
                    self.build(inventory)
                self.assertFalse(self.output.exists())

    def test_boolean_version_cannot_impersonate_integer_version(self):
        self.data['rules'][0]['rule_version'] = 1
        self.prepare()
        result = json.loads(self.result.read_text())
        result['lines'][0]['rule_version'] = True
        self.result.write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, 'differs'):
            export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())

    def test_result_number_cannot_impersonate_exact_decimal_string(self):
        self.prepare()
        result = json.loads(self.result.read_text())
        result['lines'][0]['expected_amount'] = 40.002205
        self.result.write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, 'differs'):
            export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())

    def test_original_integer_version_and_decimal_input_contract_still_work(self):
        self.data['rules'][0]['rule_version'] = 1
        inventory = self.inventory()
        for row in inventory['sources']:
            row['source_sha256'] = row['current_sha256'] = '1' * 64
        payload = self.build(inventory)
        self.assertEqual(payload['schedules']['entitlement-lines'][0]['rule_version_ref'], export.alias('version', '1'))
        self.assertEqual(payload['controls']['freshness'], 'current_as_supplied')

    def test_write_failure_removes_partial_output_and_can_retry(self):
        from unittest.mock import patch
        self.prepare()
        before = [self.source.read_bytes(), self.result.read_bytes()]
        original = Path.open
        def fail_csv(path, *args, **kwargs):
            if path.name == 'calculation-bridge.csv' and args and args[0] == 'w':
                raise OSError('synthetic disk full')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', fail_csv):
            with self.assertRaisesRegex(OSError, 'disk full'):
                export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())
        self.assertEqual(before, [self.source.read_bytes(), self.result.read_bytes()])
        export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertTrue((self.output / 'manifest.json').is_file())

    def test_adjustment_bridge_output_grows_linearly_and_resolves_line_evidence(self):
        sizes, payloads = [], []
        for count in (64, 128):
            self.data['recoupment_accounts'] = []
            self.data['lines'][0]['adjustments'] = [
                {'adjustment_id': f'ADJ-{index:04}', 'kind': 'deduction', 'amount': '-0.00001',
                 'evidence_refs': [f'synthetic-adjustment:{index:04}']}
                for index in range(count)
            ]
            self.output = self.root / f'growth-{count}'
            payload = self.build()
            sizes.append(sum(path.stat().st_size for path in self.output.iterdir()))
            payloads.append(payload)
        # Doubling adjustments/references must not quadruple serialized output.
        self.assertLess(sizes[1], sizes[0] * 2.5, sizes)
        for count, payload in zip((64, 128), payloads):
            line = payload['schedules']['entitlement-lines'][0]
            bridges = payload['schedules']['calculation-bridge']
            self.assertEqual(len(bridges), count + 3)
            self.assertEqual(len(line['evidence_refs']), count + 2)
            self.assertTrue(set(line['evidence_refs']).issubset(
                {row['evidence_ref'] for row in payload['schedules']['evidence']}))
            for step, row in enumerate(bridges):
                self.assertNotIn('evidence_refs', row)
                self.assertEqual(row['step'], step)
                for key in ('line_ref', 'rule_ref', 'rule_version_ref', 'currency',
                            'period_start', 'period_end', 'freshness', 'as_of'):
                    self.assertEqual(row[key], line[key])
            from decimal import Decimal
            self.assertEqual(Decimal(line['expected_amount']), Decimal('45.002205') - Decimal(count) * Decimal('0.00001'))

    def test_rule_version_alias_preserves_supported_json_types(self):
        aliases = []
        for index, version in enumerate((1, '1', True, 'true')):
            self.data['rules'][0]['rule_version'] = version
            self.output = self.root / f'version-{index}'
            payload = self.build()
            aliases.append(payload['schedules']['entitlement-lines'][0]['rule_version_ref'])
        self.assertEqual(len(set(aliases)), 4)

    def test_empty_schedules_keep_their_full_csv_headers(self):
        self.build()
        def headers():
            return {path.stem: next(csv.reader(path.read_text().splitlines())) for path in self.output.glob('*.csv')}
        original = headers()
        self.assertIn('record_ref', original['unresolved'])
        self.data['rules'][0]['unsupported_terms'] = 'manual interpretation'
        self.output = self.root / 'partial'
        self.build()
        self.assertEqual(headers(), original)
        self.data.update(rules=[], lines=[], recoupment_accounts=[])
        self.output = self.root / 'empty'
        payload = self.build()
        self.assertEqual(headers(), original)
        self.assertTrue(all(not rows for rows in payload['schedules'].values()))
        self.assertEqual(payload['controls']['result_status'], 'partial')

    def test_equivalent_valid_iso_dates_use_same_day_semantics(self):
        inventory = self.inventory()
        for row in inventory['sources']:
            row['checked_on'] = '20261118'
        payload = self.build(inventory)
        self.assertEqual(payload['controls']['freshness'], 'current_as_supplied')
        self.assertEqual(payload['controls']['source_control'], 'not_verified_by_exporter')
        rows = export.evidence_rows({'source'}, {'schema_version': '1', 'sources': [{
            'evidence_ref': 'source', 'source_sha256': 'a'*64, 'current_sha256': 'a'*64,
            'checked_on': '2026-11-18'}]}, '20261118')
        self.assertEqual(rows['source']['freshness'], 'current_as_supplied')

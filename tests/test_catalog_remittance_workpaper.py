"""Synthetic remittance export contracts; no provider or account access."""
import copy
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/recoup-catalog-review-deal/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('remittance_export', SCRIPTS / 'build-remittance-workpaper.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class RemittanceWorkpaperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = json.loads((SCRIPTS.parent / 'fixtures/finance/remittance-input.json').read_text())
        self.source, self.result, self.output = [self.root / name for name in ('input.json', 'result.json', 'export')]

    def prepare(self):
        self.source.write_text(json.dumps(self.data))
        self.result.write_text(export.dumps(export.calculator.reconcile(self.data)))

    def build(self, inventory=None):
        self.prepare()
        path = None
        if inventory is not None:
            path = self.root / 'evidence.json'
            path.write_text(json.dumps(inventory))
        before = [p.read_bytes() for p in (self.source, self.result)]
        manifest = export.build(self.source, self.result, self.output, '2026-11-18', path)
        self.assertEqual(before, [p.read_bytes() for p in (self.source, self.result)])
        expected = {name + '.csv' for name in export.FIELDS} | {'workpaper.json', 'report.md'}
        self.assertEqual({p['file'] for p in manifest['files']}, expected)
        self.assertEqual(len(manifest['files']), len(expected))
        self.assertEqual({p.name for p in self.output.iterdir()}, expected | {'manifest.json'})
        for p in manifest['files']:
            self.assertEqual(p['sha256'], export.common.digest((self.output / p['file']).read_bytes()))
        return json.loads((self.output / 'workpaper.json').read_text())

    def test_exact_bridge_totals_and_period_lineage(self):
        p = self.build(); s = p['schedules']; c = p['controls']
        self.assertEqual(s['verified-receipts'][0]['amount'], '97')
        self.assertEqual(s['verified-receipts'][0]['allocation_refs'], [export.alias('allocation', 'ALLOC-B')])
        self.assertEqual(s['allocations'][1]['adjustments'], '-3')
        self.assertEqual(s['adjustments'][0]['amount'], '-3')
        self.assertEqual(s['adjustments'][0]['allocation_ref'], s['allocations'][1]['allocation_ref'])
        records = {r['record_ref']: r for r in s['records']}
        first, second = s['allocations']
        self.assertEqual(first['to_record_ref'], second['from_record_ref'])
        self.assertEqual(records[first['from_record_ref']]['period_start'], '2024-01-01')
        self.assertIsNone(records[second['to_record_ref']]['period_start'])
        self.assertEqual(records[second['to_record_ref']]['date'], '2024-06-03')
        self.assertIsNone(c['current_payable']); self.assertIsNone(c['recovered_cash'])
        self.assertEqual(c['recovery_rollup'], 'not_calculated')
        self.assertEqual(c['freshness'], 'unknown')
        self.assertEqual(c['result_status'], 'ok')
        self.assertNotEqual(c['readiness'], 'ready')
        expected = json.loads(self.result.read_text())
        for got, original in zip(s['allocations'], expected['allocations']):
            for key in ('stage', 'from_amount', 'from_currency', 'to_amount', 'to_currency', 'fx_rate', 'adjustments', 'status'):
                self.assertEqual(got[key], original[key])
        for got, original in zip(s['residuals'], expected['residuals']):
            for key in ('stage', 'side', 'currency', 'amount', 'allocated', 'unallocated'):
                self.assertEqual(got[key], original[key])

    def test_user_reported_posted_is_not_verified_cash(self):
        self.data['receipts'][0]['evidence_status'] = 'user_reported'
        p = self.build()
        self.assertEqual(p['schedules']['allocations'][1]['status'], 'user_reported_receipt_unverified')
        self.assertEqual(p['schedules']['verified-receipts'], [])
        self.assertEqual(p['controls']['result_status'], 'partial')
        self.assertEqual(p['controls']['unverified_allocation_refs'], [export.alias('allocation', 'ALLOC-B')])

    def test_pending_and_account_mismatch_preserve_unresolved_unknowns(self):
        self.data['receipts'][0]['status'] = 'pending'
        p = self.build()
        self.assertEqual(len(p['schedules']['unresolved']), 1)
        self.assertIsNone(p['schedules']['unresolved'][0]['amount'])
        self.assertEqual(p['controls']['missing_required_stages'], ['remittance_to_receipt'])
        self.assertEqual(p['controls']['unmatched_required_records'], 2)
        self.assertEqual(p['schedules']['verified-receipts'], [])

    def test_statement_only_scope_is_not_cash_completion(self):
        self.data['completion_scope'] = ['statement_to_remittance']
        self.data['allocations'] = self.data['allocations'][:1]
        p = self.build()
        self.assertEqual(p['controls']['result_status'], 'ok')
        self.assertEqual(p['schedules']['verified-receipts'], [])
        self.assertTrue(any(not row['in_completion_scope'] for row in p['schedules']['residuals']))
        self.assertIsNone(p['controls']['current_payable'])

    def test_returns_net_zero_and_sparse_currency_totals(self):
        original = copy.deepcopy(self.data)
        for name in ('statements', 'remittances', 'receipts'):
            row = copy.deepcopy(original[name][0]); row['id'] += '-RETURN'; row['source_record_id'] += '-RETURN'
            row['amount'] = '-' + row['amount']; self.data[name].append(row)
        for row in original['allocations']:
            row['allocation_id'] += '-RETURN'; row['from_id'] += '-RETURN'; row['to_id'] += '-RETURN'
            row['from_amount'] = '-' + row['from_amount']; row['to_amount'] = '-' + row['to_amount']
            for adj in row.get('adjustments', []):
                adj['kind'] = 'supported_adjustment'; adj['amount'] = '3'
            self.data['allocations'].append(row)
        p = self.build()
        self.assertEqual(p['schedules']['verified-receipts'][0]['amount'], '0')
        self.assertEqual(p['schedules']['verified-receipts'][0]['allocation_refs'],
                         [export.alias('allocation', 'ALLOC-B'), export.alias('allocation', 'ALLOC-B-RETURN')])
        self.assertEqual(p['schedules']['allocations'][-1]['status'], 'verified_return')
        self.assertEqual(p['schedules']['allocations'][-1]['to_amount'], '-97')
        with (self.output / 'allocations.csv').open() as f:
            self.assertEqual(list(csv.DictReader(f))[-1]['to_amount'], "'-97")

    def test_fx_and_subcent_separate_currency_evidence(self):
        self.data['receipts'][0].update(currency='EUR', amount='90.000000000000000001')
        edge = self.data['allocations'][1]
        edge.update(fx_rate='0.9', fx_evidence_refs=['synthetic:fx'], to_amount='90.000000000000000001',
                    adjustments=[{'adjustment_id': 'subcent', 'kind': 'supported_adjustment', 'currency': 'EUR',
                                  'amount': '0.000000000000000001', 'evidence_refs': ['synthetic:adjustment']}])
        p = self.build(); row = p['schedules']['allocations'][1]
        self.assertEqual(row['fx_rate'], '0.9')
        self.assertEqual(row['from_currency'], 'USD'); self.assertEqual(row['to_currency'], 'EUR')
        self.assertEqual(row['fx_evidence_refs'], [export.common.alias('evidence', 'synthetic:fx')])
        self.assertEqual(p['schedules']['verified-receipts'][0]['amount'], '90.000000000000000001')
        self.assertEqual(p['schedules']['verified-receipts'][0]['currency'], 'EUR')

    def test_large_integer_no_float_rounding(self):
        for name in ('statements', 'remittances', 'receipts'):
            self.data[name][0]['amount'] = '9007199254740993'
        for row in self.data['allocations']:
            row.update(from_amount='9007199254740993', to_amount='9007199254740993', adjustments=[])
        self.assertEqual(self.build()['schedules']['verified-receipts'][0]['amount'], '9007199254740993')

    def test_privacy_and_typed_aliases(self):
        self.data['receiving_account_access'] = 'PRIVATE_ACCESS'
        for name in ('statements', 'remittances', 'receipts'):
            self.data[name][0].update(name='PRIVATE_NAME', location='/PRIVATE', source_version={'private': 'PRIVATE_VERSION'},
                                     evidence_refs=['https://PRIVATE/token=SECRET'])
        self.data['remittances'][0]['receiving_account_ref'] = 'PRIVATE_ACCOUNT'
        self.data['receipts'][0]['account_ref'] = 'PRIVATE_ACCOUNT'
        self.data['remittances'][0]['status'] = {'private': 'PRIVATE_STATUS'}
        self.data['allocations'][0]['from_amount'] = '101' # error contains source id; never copy error prose
        self.build()
        combined = ''.join(p.read_text() for p in self.output.iterdir())
        self.assertNotIn('PRIVATE', combined); self.assertNotIn('SECRET', combined)
        self.assertEqual(len({export.alias('version', v) for v in (1, '1', True)}), 3)

    def test_empty_fixed_headers_and_unknowns(self):
        for key in ('statements', 'remittances', 'receipts', 'allocations'):
            self.data[key] = []
        p = self.build()
        self.assertEqual(p['controls']['result_status'], 'partial')
        for name, fields in export.FIELDS.items():
            with (self.output / (name + '.csv')).open() as f:
                self.assertEqual(next(csv.reader(f)), list(fields))

    def test_result_tampering_json_types_rejected_before_write(self):
        self.prepare(); original = json.loads(self.result.read_text())
        for key, value in [('unmatched_required_records', False), ('current_payable', 0), ('status', 'partial')]:
            with self.subTest(key=key):
                changed = copy.deepcopy(original); changed[key] = value
                self.result.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    export.build(self.source, self.result, self.output, '2026-11-18')
                self.assertFalse(self.output.exists())

    def test_no_overwrite_and_private_permissions(self):
        old = os.umask(0o022)
        try:
            self.build()
        finally:
            os.umask(old)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        for path in self.output.iterdir():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        before = (self.output / 'manifest.json').read_bytes()
        with self.assertRaises(ValueError):
            export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertEqual(before, (self.output / 'manifest.json').read_bytes())
        link = self.root / 'link'; link.symlink_to(self.output, target_is_directory=True)
        with self.assertRaises(ValueError):
            export.build(self.source, self.result, link, '2026-11-18')

    def test_failed_write_cleans_only_new_destination(self):
        self.prepare()
        with patch.object(export.csv.DictWriter, 'writerow', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists()); self.assertTrue(self.source.exists()); self.assertTrue(self.result.exists())

    def test_freshness_stale_unknown_and_supplied_current(self):
        refs = set()
        for name in ('statements', 'remittances', 'receipts', 'allocations'):
            for row in self.data[name]:
                refs.update(row['evidence_refs'])
                for adj in row.get('adjustments', []): refs.update(adj['evidence_refs'])
        inventory = {'schema_version': '1', 'sources': [{'evidence_ref': ref, 'source_sha256': 'a'*64,
                      'current_sha256': 'a'*64, 'checked_on': '2026-11-18'} for ref in sorted(refs)]}
        for status in ('current_as_supplied', 'stale', 'unknown'):
            with self.subTest(status=status):
                if status == 'stale': inventory['sources'][0]['current_sha256'] = 'b'*64
                if status == 'unknown': inventory['sources'] = []
                p = self.build(inventory)
                self.assertEqual(p['controls']['freshness'], status)
                self.assertEqual(p['controls']['source_control'], 'not_verified_by_exporter')
                shutil.rmtree(self.output)

    def test_linear_shared_record_evidence(self):
        sizes = []
        for n in (32, 64):
            self.data['statements'][0]['amount'] = str(n)
            self.data['remittances'][0]['amount'] = str(n)
            self.data['statements'][0]['evidence_refs'] = ['synthetic:source:'+str(i) for i in range(n)]
            self.data['receipts'] = []
            self.data['completion_scope'] = ['statement_to_remittance']
            self.data['allocations'] = [{'allocation_id': str(i), 'stage': 'statement_to_remittance', 'from_id': 'ST-A',
                'to_id': 'PAY-A', 'from_amount': '1', 'to_amount': '1', 'evidence_refs': ['synthetic:edge:'+str(i)]} for i in range(n)]
            p = self.build(); sizes.append((self.output / 'workpaper.json').stat().st_size)
            self.assertEqual(len(p['schedules']['allocations'][0]['evidence_refs']), 1)
            shutil.rmtree(self.output)
        self.assertLess(sizes[1] / sizes[0], 2.2)

    def test_contributor_links_exclude_unverified_and_grow_linearly(self):
        sizes = []
        for n in (32, 64):
            for name in ('statements', 'remittances'):
                self.data[name][0]['amount'] = str(n + 1)
            receipt = self.data['receipts'][0]
            receipt['amount'] = str(n)
            receipt['evidence_refs'] = ['synthetic:receipt:' + str(i) for i in range(n)]
            user = copy.deepcopy(receipt)
            user.update(id='USER', source_record_id='USER-SOURCE', amount='1', evidence_status='user_reported')
            self.data['receipts'] = [receipt, user]
            self.data['allocations'] = [{'allocation_id': 'edge-' + str(i), 'stage': 'remittance_to_receipt',
                'from_id': 'PAY-A', 'to_id': 'BANK-A' if i < n else 'USER', 'from_amount': '1',
                'to_amount': '1', 'evidence_refs': ['synthetic:allocation:' + str(i)]} for i in range(n + 1)]
            p = self.build()
            total = p['schedules']['verified-receipts'][0]
            self.assertEqual(total['amount'], str(n))
            self.assertEqual(total['allocation_refs'], [export.alias('allocation', 'edge-' + str(i)) for i in range(n)])
            self.assertEqual(p['controls']['result_status'], 'partial')
            sizes.append((self.output / 'workpaper.json').stat().st_size)
            shutil.rmtree(self.output)
        self.assertLess(sizes[1] / sizes[0], 2.2)

    def test_multiple_currencies_remain_separate(self):
        for name in ('statements', 'remittances', 'receipts'):
            row = copy.deepcopy(self.data[name][0])
            row.update(id=row['id']+'-EUR', source_record_id=row['source_record_id']+'-EUR', currency='EUR')
            self.data[name].append(row)
        for original in list(self.data['allocations']):
            row = copy.deepcopy(original)
            row.update(allocation_id=row['allocation_id']+'-EUR', from_id=row['from_id']+'-EUR', to_id=row['to_id']+'-EUR')
            for adj in row.get('adjustments', []): adj['currency'] = 'EUR'
            self.data['allocations'].append(row)
        rows = self.build()['schedules']['verified-receipts']
        self.assertEqual({r['currency']: r['amount'] for r in rows}, {'USD': '97', 'EUR': '97'})
        self.assertEqual({r['currency']: r['allocation_refs'] for r in rows},
                         {'USD': [export.alias('allocation', 'ALLOC-B')],
                          'EUR': [export.alias('allocation', 'ALLOC-B-EUR')]})

    def test_wrong_account_and_missing_fx_evidence_never_create_cash(self):
        for mode in ('account', 'fx'):
            with self.subTest(mode=mode):
                if mode == 'account': self.data['receipts'][0]['account_ref'] = 'different'
                else:
                    self.data['receipts'][0].update(account_ref='ACCOUNT-A', currency='EUR')
                    self.data['allocations'][1]['fx_rate'] = '1'
                    self.data['allocations'][1]['adjustments'][0]['currency'] = 'EUR'
                p = self.build()
                self.assertEqual(p['schedules']['verified-receipts'], [])
                self.assertEqual(p['controls']['result_status'], 'partial')
                self.assertEqual(len(p['schedules']['unresolved']), 1)
                shutil.rmtree(self.output)

    def test_invalid_evidence_and_input_fail_without_output(self):
        for changes in ({'source_sha256': 1}, {'checked_on': '2026-11-19'}, {'checked_on': 'not-a-date'}):
            inventory = {'schema_version': '1', 'sources': [{'evidence_ref': 'synthetic-royalty:page-1', **changes}]}
            with self.assertRaises(ValueError): self.build(inventory)
            self.assertFalse(self.output.exists())
        self.data['receiving_account_access'] = []
        self.source.write_text(json.dumps(self.data)); self.result.write_text('{}')
        with self.assertRaises(ValueError): export.build(self.source, self.result, self.output, '2026-11-18')
        self.assertFalse(self.output.exists())

    def test_new_calculation_example_private_and_refuses_repeat(self):
        self.prepare()
        # Run exactly the documented private directory creation pattern with synthetic paths.
        command = '( umask 077 && mkdir -m 700 remittance-run-v2 && python3 calculator.py --input input.json --output remittance-run-v2/result.json )'
        shutil.copyfile(SCRIPTS / 'reconcile-remittances.py', self.root / 'calculator.py')
        shutil.copyfile(SCRIPTS / '_finance.py', self.root / '_finance.py')
        p = subprocess.run(command, shell=True, cwd=self.root, capture_output=True)
        self.assertEqual(p.returncode, 0)
        directory = self.root / 'remittance-run-v2'; result = directory / 'result.json'
        self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
        self.assertEqual(result.stat().st_mode & 0o777, 0o600)
        before = result.read_bytes()
        p = subprocess.run(command, shell=True, cwd=self.root, capture_output=True)
        self.assertNotEqual(p.returncode, 0); self.assertEqual(result.read_bytes(), before)

    def test_standalone_cli_without_repository_imports(self):
        self.prepare(); local = self.root / 'standalone'; local.mkdir()
        for name in ('build-remittance-workpaper.py', 'build-royalty-workpaper.py', 'reconcile-remittances.py', '_finance.py'):
            shutil.copyfile(SCRIPTS / name, local / name)
        p = subprocess.run([sys.executable, str(local / 'build-remittance-workpaper.py'), '--input', str(self.source),
            '--result', str(self.result), '--as-of', '2026-11-18', '--output-directory', str(self.output)],
            cwd='/tmp', env={**os.environ, 'PYTHONPATH': ''}, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads((self.output / 'workpaper.json').read_text())['schedules']['verified-receipts'][0]['amount'], '97')


if __name__ == '__main__':
    unittest.main()

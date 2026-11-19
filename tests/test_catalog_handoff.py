"""Bounded selective assembly over synthetic immutable helper exports."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/recoup-catalog-review-deal/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('handoff', SCRIPTS / 'assemble-catalog-handoff.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.selection = self.root / 'selection.json'
        self.output = self.root / 'handoff'
        self.entries = []

    def financial(self, kind, mutate=None, inventory=None):
        module = export.royalty if kind == 'entitlement' else export.remittance
        fixture = 'entitlement-input.json' if kind == 'entitlement' else 'remittance-input.json'
        data = json.loads((SCRIPTS.parent / 'fixtures/finance' / fixture).read_text())
        if mutate:
            mutate(data)
        source, result = self.root / (kind + '-input.json'), self.root / (kind + '-result.json')
        source.write_text(json.dumps(data))
        calculated = module.calculator().calculate(data) if kind == 'entitlement' else module.calculator.reconcile(data)
        result.write_text(module.dumps(calculated))
        evidence = None
        if inventory:
            evidence = self.root / 'inventory.json'
            evidence.write_text(json.dumps(inventory))
        directory = self.root / kind
        module.build(source, result, directory, '2026-11-18', evidence)
        self.add(kind, directory)
        return directory

    def case(self):
        case = {'schema_version': 1, 'case_id': 'PRIVATE_CASE', 'revision': 3,
                **{name: {} for name in export.case_export.COLLECTIONS}}
        case['sources']['PRIVATE_SOURCE'] = {'id': 'PRIVATE_SOURCE', 'status': 'active', 'location': '/PRIVATE_PATH/SECRET'}
        case['findings']['PRIVATE_FINDING'] = {'id': 'PRIVATE_FINDING', 'stage': 'reconcile', 'status': 'open', 'stale': True,
            'source_refs': [{'source_id': 'PRIVATE_SOURCE', 'version': 'PRIVATE_VERSION'}], 'evidence_gap': 'SECRET_GAP', 'cause_id': 'PRIVATE_CAUSE'}
        case['attempts']['a'] = {'id': 'a', 'status': 'rejected', 'action_id': 'action', 'payload': 'SECRET'}
        source = self.root / 'case.json'
        source.write_text(json.dumps(case))
        directory = self.root / 'case'
        export.case_export.build(source, directory)
        self.add('case', directory)
        return directory

    def add(self, kind, directory):
        self.entries.append({'kind': kind, 'directory': str(directory), 'manifest_sha256': export.sha((directory / 'manifest.json').read_bytes())})

    def build(self):
        self.selection.write_text(json.dumps({'schema_version': '1', 'exports': self.entries}))
        return export.build(self.selection, self.output)

    def rehash(self, directory):
        path = directory / 'manifest.json'
        m = json.loads(path.read_text())
        for entry in m['files']:
            entry['sha256'] = export.sha((directory / entry['file']).read_bytes())
        path.write_text(json.dumps(m))
        for entry in self.entries:
            if entry['directory'] == str(directory):
                entry['manifest_sha256'] = export.sha(path.read_bytes())

    def test_all_scopes_exact_financial_values_and_case_links(self):
        first = self.financial('entitlement')
        second = self.financial('remittance')
        self.case()
        before = {p: p.read_bytes() for d in (first, second) for p in d.iterdir()}
        manifest = self.build()
        for p, raw in before.items():
            self.assertEqual(p.read_bytes(), raw)
        for kind, source in (('entitlement', first), ('remittance', second)):
            original = json.loads((source / 'workpaper.json').read_text())
            assembled = json.loads((self.output / kind / 'workpaper.json').read_text())
            self.assertEqual(assembled['controls'], original['controls'])
            self.assertEqual(assembled['schedules'], original['schedules'])
        case = json.loads((self.output / 'case/workpaper.json').read_text())
        self.assertEqual(case['schedules']['sources'][0]['id'], case['schedules']['findings'][0]['source_refs'][0]['source_id'])
        self.assertTrue(case['schedules']['findings'][0]['stale'])
        self.assertEqual(case['schedules']['attempts'][0]['status'], 'rejected')
        for entry in manifest['files']:
            self.assertEqual(entry['sha256'], export.sha((self.output / entry['file']).read_bytes()))
        text = ''.join(p.read_text() for p in self.output.rglob('*') if p.is_file())
        for secret in ('PRIVATE', 'SECRET', str(self.root)):
            self.assertNotIn(secret, text)
        self.assertIn('not_calculated', text)
        self.assertIn('not_performed', text)

    def test_selective_scope_does_not_read_unselected_inputs(self):
        self.financial('entitlement')
        (self.root / 'remittance').mkdir()
        (self.root / 'remittance/manifest.json').write_text('SECRET NOT JSON')
        self.build()
        handoff = json.loads((self.output / 'handoff.json').read_text())
        self.assertEqual(handoff['excluded_stages'], ['case', 'remittance'])
        self.assertFalse((self.output / 'remittance').exists())

    def test_partial_out_of_scope_and_unknown_are_preserved(self):
        def change(data):
            data['receipts'][0]['evidence_status'] = 'user_reported'
            data['completion_scope'] = ['statement_to_remittance']
        source = self.financial('remittance', change)
        self.build()
        original = json.loads((source / 'workpaper.json').read_text())
        result = json.loads((self.output / 'remittance/workpaper.json').read_text())
        self.assertEqual(original['controls'], result['controls'])
        self.assertEqual(original['schedules'], result['schedules'])
        self.assertIsNone(result['controls']['recovered_cash'])
        self.assertEqual(result['controls']['freshness'], 'unknown')
        self.assertFalse(result['schedules']['allocations'][1]['in_completion_scope'])

    def test_tampering_manifest_member_and_helper_versions_refused(self):
        directory = self.financial('entitlement')
        original = {p: p.read_bytes() for p in directory.iterdir()}
        for name, replacement, rehash in (
            ('report.md', b'changed', False),
            ('manifest.json', b'{}', False),
            ('entitlement-lines.csv', b'wrong,header\n', True),
        ):
            with self.subTest(name=name):
                (directory / name).write_bytes(replacement)
                if rehash:
                    self.rehash(directory)
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())
                for p, raw in original.items():
                    p.write_bytes(raw)
                self.entries[0]['manifest_sha256'] = export.sha(original[directory / 'manifest.json'])
        m = json.loads((directory / 'manifest.json').read_text())
        m['exporter_sha256'] = '0' * 64
        (directory / 'manifest.json').write_text(json.dumps(m))
        self.entries[0]['manifest_sha256'] = export.sha((directory / 'manifest.json').read_bytes())
        with self.assertRaises(ValueError):
            self.build()

    def test_private_extensions_discarded_and_known_field_injection_rejected(self):
        directory = self.financial('entitlement')
        p = directory / 'workpaper.json'
        data = json.loads(p.read_text())
        data['private'] = {'token': 'SECRET_TOKEN'}
        data['controls']['source_path'] = '/SECRET_PATH'
        data['schedules']['entitlement-lines'][0]['private'] = 'SECRET_FIELD'
        p.write_text(json.dumps(data)); self.rehash(directory)
        self.build()
        self.assertNotIn('SECRET', (self.output / 'entitlement/workpaper.json').read_text())
        shutil.rmtree(self.output)
        data['schedules']['entitlement-lines'][0]['freshness'] = 'SECRET_STATUS'
        p.write_text(json.dumps(data)); self.rehash(directory)
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_stale_negative_large_and_subcent_amounts_are_not_rounded(self):
        def change(data):
            data['lines'][0]['reported_amount'] = '9007199254740993.000001'
        inventory = {'schema_version': '1', 'sources': [{'evidence_ref': 'statement-line-1', 'source_sha256': 'a' * 64, 'current_sha256': 'b' * 64, 'checked_on': '2026-11-18'}]}
        # Use actual fixture evidence reference, not an assumed reference name.
        fixture = json.loads((SCRIPTS.parent / 'fixtures/finance/entitlement-input.json').read_text())
        inventory['sources'][0]['evidence_ref'] = fixture['lines'][0]['evidence_refs'][0]
        directory = self.financial('entitlement', change, inventory)
        self.build()
        result = json.loads((self.output / 'entitlement/workpaper.json').read_text())
        original = json.loads((directory / 'workpaper.json').read_text())
        self.assertEqual(result['schedules'], original['schedules'])
        self.assertEqual(result['controls']['freshness'], 'stale')
        self.assertEqual(result['schedules']['entitlement-lines'][0]['reported_amount'], '9007199254740993.000001')
        self.assertIn("'-", (self.output / 'entitlement/entitlement-lines.csv').read_text())

    def test_supported_exponent_input_spelling_preserved(self):
        def change(data):
            data['rules'][0]['participation_rate'] = '5e-1'
            data['rules'][0]['commission_rate'] = '+.2'
        directory = self.financial('entitlement', change)
        self.build()
        original = json.loads((directory / 'workpaper.json').read_text())
        result = json.loads((self.output / 'entitlement/workpaper.json').read_text())
        self.assertEqual(result['schedules'], original['schedules'])
        self.assertEqual(result['schedules']['entitlement-lines'][0]['participation_rate'], '5e-1')

    def test_manifest_traversal_duplicate_member_and_duplicate_scope_refused(self):
        directory = self.financial('entitlement')
        path = directory / 'manifest.json'
        original = json.loads(path.read_text())
        for name in ('../private', '/absolute', 'workpaper.json'):
            m = copy.deepcopy(original)
            m['files'][0]['file'] = name
            path.write_text(json.dumps(m))
            self.entries[0]['manifest_sha256'] = export.sha(path.read_bytes())
            with self.assertRaises(ValueError):
                self.build()
            self.assertFalse(self.output.exists())
        path.write_text(json.dumps(original))
        self.entries[0]['manifest_sha256'] = export.sha(path.read_bytes())
        self.entries.append(self.entries[0].copy())
        with self.assertRaises(ValueError):
            self.build()

    def test_source_mutation_after_admission_does_not_change_output(self):
        directory = self.financial('entitlement')
        original = (directory / 'workpaper.json').read_bytes()
        method = export.financial
        def mutate(*args):
            (directory / 'workpaper.json').write_text('changed after snapshot')
            return method(*args)
        with patch.object(export, 'financial', side_effect=mutate):
            self.build()
        result = json.loads((self.output / 'entitlement/workpaper.json').read_text())
        self.assertEqual(result['schedules'], json.loads(original)['schedules'])

    def test_duplicate_keys_unsupported_schema_and_paths(self):
        directory = self.financial('entitlement')
        self.selection.write_text('{"schema_version":"1","schema_version":"1","exports":[]}')
        with self.assertRaises(ValueError):
            export.build(self.selection, self.output)
        for change in ({'kind': 'normalization'}, {'directory': str(self.root / 'absent')}, {'manifest_sha256': 'x'}):
            entry = self.entries[0].copy()
            self.entries[0].update(change)
            with self.assertRaises((ValueError, OSError)):
                self.build()
            self.entries[0] = entry
        self.output = directory / 'new'
        with self.assertRaises(ValueError):
            self.build()

    def test_existing_destination_symlinks_permissions_and_failure_cleanup(self):
        directory = self.financial('entitlement')
        self.output.mkdir()
        (self.output / 'keep').write_text('keep')
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual((self.output / 'keep').read_text(), 'keep')
        shutil.rmtree(self.output)
        target = directory / 'report.md'
        saved = self.root / 'saved-report'
        target.rename(saved); target.symlink_to(saved)
        with self.assertRaises(ValueError):
            self.build()
        target.unlink(); saved.rename(target)
        original_write = export.write
        def fail(path, text):
            if path.name.endswith('.csv'):
                raise OSError('synthetic write failure')
            return original_write(path, text)
        with patch.object(export, 'write', side_effect=fail):
            with self.assertRaises(OSError):
                self.build()
        self.assertFalse(self.output.exists())
        self.build()
        for path in (self.output, *self.output.rglob('*')):
            self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)

    def test_limits_preflight_and_row_limit(self):
        directory = self.financial('entitlement')
        with patch.object(export, 'MAX_TOTAL', 20):
            with self.assertRaises(ValueError):
                self.build()
        with patch.object(export, 'MAX_ROWS', 1):
            with self.assertRaises(ValueError):
                self.build()
        large = self.root / 'large'
        large.write_bytes(b'x' * 100)
        with patch.object(Path, 'open', side_effect=AssertionError('must reject before read')):
            with self.assertRaises(ValueError):
                export.read(large, [0], 50)
        self.assertFalse(self.output.exists())

    def test_assembly_does_not_execute_financial_calculators(self):
        self.financial('entitlement')
        self.financial('remittance')
        with patch.object(export.royalty, 'calculator', side_effect=AssertionError('no new math')), patch.object(export.remittance.calculator, 'reconcile', side_effect=AssertionError('no new math')):
            self.build()

    def test_new_session_cli_and_standalone_skill(self):
        self.financial('remittance')
        self.selection.write_text(json.dumps({'schema_version': '1', 'exports': self.entries}))
        skill = self.root / 'standalone'
        shutil.copytree(SCRIPTS.parent, skill)
        result = subprocess.run([sys.executable, str(skill / 'scripts/assemble-catalog-handoff.py'), '--selection', str(self.selection), '--output-directory', str(self.output)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        handoff = json.loads((self.output / 'handoff.json').read_text())
        for entry in handoff['exports']:
            payload = json.loads((self.output / entry['workpaper']).read_text())
            self.assertEqual(payload['input_manifest_sha256'], entry['input_manifest_sha256'])
            self.assertEqual(payload['controls'], entry['controls'])
        self.assertFalse(handoff['publication_authorized'])


if __name__ == '__main__':
    unittest.main()

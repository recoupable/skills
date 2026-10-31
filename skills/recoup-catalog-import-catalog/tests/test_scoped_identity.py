import csv
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('intake', Path(__file__).parents[1] / 'scripts/import_catalog.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ScopedIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'synthetic.csv'
        self.mapping = {'entities': {'composition': {
            'title': 'Title', 'provider_id': 'Work', 'provider_namespace': 'Provider',
            'account_scope': 'Account', 'iswc': 'ISWC', 'writers': 'Writers'}},
            'interest': {'kind': 'Kind', 'value': 'Share', 'basis': 'Basis', 'scale': 'Scale', 'parent_reference': 'Parent'}}
        self.row = ['Twin', 'WORK-1', 'mlc', 'member-A', 'T0000000001', 'Writer A', 'collection', '50', 'provider_claim', '100', 'P1']

    def run_rows(self, rows, previous=None):
        with self.source.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['Title', 'Work', 'Provider', 'Account', 'ISWC', 'Writers', 'Kind', 'Share', 'Basis', 'Scale', 'Parent'])
            writer.writerows(rows)
        return MOD.intake(self.source, self.mapping, previous=previous)

    def test_conflicting_iswc_and_writers_hold_all_observations_and_preserve_lineage(self):
        other = self.row.copy()
        other[4:6] = ['T0000000002', 'Writer B']
        other[-1] = 'P2'
        rows = [self.row, other, self.row]
        packet = self.run_rows(rows)
        self.assertEqual(packet['controls']['dispositions'], {'held': 3})
        for row, raw in zip(packet['rows'], rows):
            self.assertEqual(row['raw_values'], raw)
            self.assertTrue(any('scoped provider identity' in reason for reason in row['reasons']))
        self.assertEqual([r['locator']['row'] for r in packet['rows']], [2, 3, 4])
        observations = [o for e in packet['entities'] for o in e['observations']]
        self.assertEqual(len(observations), 3)
        self.assertEqual({o['source_version'] for o in observations}, {hashlib.sha256(self.source.read_bytes()).hexdigest()})
        self.assertEqual({o['row_id'] for o in observations}, {r['row_id'] for r in packet['rows']})
        self.assertTrue(all(e['identity_status'] == 'conflicting_observations' for e in packet['entities']))
        self.assertEqual([i['fields']['parent_reference'] for i in packet['interest_observations']], ['P1', 'P2', 'P1'])
        self.assertEqual([i['fields']['value'] for i in packet['interest_observations']], ['50'] * 3)
        self.assertNotIn('total_share', packet)
        self.assertEqual(self.run_rows(rows, packet)['controls']['dispositions'], {'held': 3})

    def test_either_iswc_or_writers_conflict_is_held(self):
        for column, value in [(4, 'T0000000002'), (5, 'Writer B')]:
            other = self.row.copy()
            other[column] = value
            with self.subTest(column=column):
                self.assertEqual(self.run_rows([self.row, other])['controls']['dispositions'], {'held': 2})

    def test_identical_observations_and_replay_stable(self):
        packet = self.run_rows([self.row, self.row])
        self.assertEqual(packet['controls']['dispositions'], {'proposed': 2})
        self.assertEqual(len(packet['entities']), 1)
        replay = self.run_rows([self.row, self.row], packet)
        self.assertEqual(replay['controls']['dispositions'], {'unchanged': 2})
        self.assertEqual(packet['entities'], replay['entities'])

    def test_distinct_account_namespace_or_work_never_collide(self):
        for column, value in [(1, 'WORK-2'), (2, 'other-provider'), (3, 'member-B')]:
            for changed_metadata in (False, True):
                other = self.row.copy()
                other[column] = value
                if changed_metadata:
                    other[5] = 'Writer B'
                with self.subTest(column=column, changed_metadata=changed_metadata):
                    packet = self.run_rows([self.row, other])
                    self.assertEqual(packet['controls']['dispositions'], {'proposed': 2})
                    self.assertEqual(len(packet['entities']), 2)

    def test_missing_scope_is_held_and_row_scoped_without_inference(self):
        for column in (2, 3):
            for value in ('', '   '):
                row = self.row.copy()
                row[column] = value
                with self.subTest(column=column, value=value):
                    packet = self.run_rows([row, row, self.row])
                    self.assertEqual(packet['controls']['dispositions'], {'held': 2, 'proposed': 1})
                    self.assertEqual(len(packet['entities']), 3)
                    self.assertFalse(any('scoped provider identity' in reason for r in packet['rows'] for reason in r['reasons']))

    def test_whitespace_provider_ids_do_not_group_unrelated_works(self):
        first = self.row.copy()
        first[1] = '   '
        second = first.copy()
        second[4:6] = ['T0000000002', 'Writer B']
        packet = self.run_rows([first, second])
        self.assertEqual(packet['controls']['dispositions'], {'held': 2})
        self.assertEqual(len(packet['entities']), 2)
        for row, raw in zip(packet['rows'], [first, second]):
            self.assertEqual(row['raw_values'], raw)
            self.assertTrue(any('provider_id' in reason for reason in row['reasons']))
            self.assertFalse(any('conflict' in reason for reason in row['reasons']))
        for entity in packet['entities']:
            self.assertEqual(entity['identity_status'], 'unresolved')
            self.assertEqual(entity['fields']['provider_id'], '   ')
            self.assertEqual(entity['observations'][0]['source_version'], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual({o['row_id'] for e in packet['entities'] for o in e['observations']}, {r['row_id'] for r in packet['rows']})

    def test_empty_provider_ids_use_distinct_supplied_iswcs_without_grouping(self):
        first = self.row.copy()
        first[1] = ''
        second = first.copy()
        second[4:6] = ['T0000000002', 'Writer B']
        packet = self.run_rows([first, second])
        self.assertEqual(packet['controls']['dispositions'], {'proposed': 2})
        self.assertEqual(len(packet['entities']), 2)
        self.assertEqual([r['raw_values'] for r in packet['rows']], [first, second])

    def test_missing_identifier_value_does_not_claim_contradiction(self):
        other = self.row.copy()
        other[4] = ''
        packet = self.run_rows([self.row, other])
        self.assertEqual(packet['controls']['dispositions'], {'proposed': 2})


if __name__ == '__main__':
    unittest.main()

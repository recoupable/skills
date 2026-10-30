import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fields', ROOT / 'scripts/mlc-public-fields.py')
fields = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fields)


class FieldTests(unittest.TestCase):
    def values(self):
        return {'subject_id': 'work1', 'work_title': 'Synthetic work',
                'writers': [{'name': 'Synthetic Writer', 'role': 'CA'}],
                'collection_shares': [{'party': 'Synthetic Publisher', 'percent': '50'}]}

    def check(self, values):
        return fields.check_fields(values, ['work1'])

    def test_public_subset_and_partial_controlled_share(self):
        result = self.check(self.values())
        self.assertEqual(result['status'], 'checked_public_subset')
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['values'], self.values())
        self.assertEqual(result['authority_verification'], 'unverified')

    def test_missing_unknown_is_not_filled(self):
        result = self.check({'subject_id': 'work1'})
        self.assertEqual(result['status'], 'needs_attention')
        self.assertEqual({f['path'] for f in result['findings']},
                         {'work_title', 'writers', 'collection_shares'})
        self.assertEqual(result['values'], {'subject_id': 'work1'})

    def test_share_bounds_and_bool_nonfinite_not_number(self):
        for value in ['0.01', '100', 50, 0.5]:
            data = self.values(); data['collection_shares'][0]['percent'] = value
            self.assertEqual(self.check(data)['findings'], [])
        for value in ['0', '-1', '100.01', True, None, 'NaN', 'Infinity', float('nan'), {}, 'unknown']:
            with self.subTest(value=value):
                data = self.values(); data['collection_shares'][0]['percent'] = value
                self.assertTrue(self.check(data)['findings'])

    def test_writer_role_and_optional_recordings(self):
        for role in ['A', 'made_up', None]:
            data = self.values(); data['writers'][0]['role'] = role
            self.assertTrue(self.check(data)['findings'])
        data = self.values(); data['recordings'] = [{'title': 'Recording'}]
        self.assertTrue(self.check(data)['findings'])
        data['recordings'][0]['artist'] = 'Synthetic Artist'
        self.assertEqual(self.check(data)['findings'], [])

    def test_no_cross_work_or_partial_batch_claim(self):
        for subjects in [['other'], ['work1', 'work2']]:
            with self.assertRaises(ValueError): fields.check_fields(self.values(), subjects)
        with self.assertRaises(ValueError): self.check({'subject_id': 'work1', 'invented': 1})

    def test_malformed_collections_return_findings(self):
        for key in ['writers', 'collection_shares', 'recordings']:
            for value in ['text', {}, [None], [True]]:
                data = self.values(); data[key] = value
                self.assertTrue(self.check(data)['findings'])


if __name__ == '__main__': unittest.main()

"""Synthetic archive safety, conservation and cross-member normalization."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('archive_normalizer', SCRIPTS / 'normalize-royalty-statement.py')
normalizer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = normalizer
spec.loader.exec_module(normalizer)


def statement(net='0.0049', currency='USD', transaction='one'):
    row = {'Title': 'Synthetic', 'ISRC': 'USZZZ2400001', 'Net': net, 'Currency': currency,
           'Period Start': '2024-01-01', 'Period End': '2024-01-31', 'Rights Type': 'master',
           'Income Type': 'streaming', 'Account ID': 'synthetic', 'Statement ID': 'q1',
           'Transaction ID': transaction}
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
    return stream.getvalue()


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root / 'statements.zip'; self.output = self.root / 'result'

    def archive(self, members):
        with zipfile.ZipFile(self.source, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in members: archive.writestr(name, data)

    def run_batch(self, **limits):
        return normalizer.normalize_archive('distributor', self.source, self.output, **limits)

    def test_order_lineage_exact_totals_revisions_and_reversals(self):
        self.archive([('03-eur.csv', statement('-0.0049', 'EUR', 'reverse')),
                      ('02-correction.csv', statement('0.0051')),
                      ('01-original.csv', statement()), ('04-repeat.csv', statement())])
        result = self.run_batch()
        self.assertEqual(result['status'], 'partial')
        self.assertEqual([m['member'] for m in result['members']], ['01-original.csv', '02-correction.csv', '03-eur.csv', '04-repeat.csv'])
        self.assertEqual(result['members'][3]['receipt']['row_conservation']['duplicate_rows'], 1)
        self.assertEqual(result['members'][1]['receipt']['row_conservation']['held'], 1)
        with (self.output / 'ledger.csv').open() as stream: rows = list(csv.DictReader(stream))
        self.assertEqual([r['owner_net_amount'] for r in rows], ['0.0049', '0.0051', '-0.0049'])
        self.assertEqual(rows[2]['currency'], 'EUR')
        self.assertIn('overlap:revised_transaction_requires_resolution', rows[1]['held_reasons'])
        self.assertTrue(rows[0]['source_file'].endswith('!/01-original.csv'))
        self.assertIn(result['archive_version_id'], rows[0]['source_file'])
        for member in result['members']:
            receipt = member['receipt']; self.assertEqual(receipt['archive_member'], member['member'])
            self.assertEqual(receipt['archive_version_id'], result['archive_version_id'])
            self.assertTrue((self.output / receipt['row_receipt']).exists())
            self.assertEqual(receipt['source_version_id'], member['source_version_id'])
        self.assertNotIn('total_amount', result)

    def test_partial_members_header_only_malformed_and_unsupported(self):
        self.archive([('a.csv', statement()), ('b.csv', statement().splitlines()[0]+'\n'),
                      ('c.csv', 'Title,Title\nx,y\n'), ('d.pdf', b'not parsed'), ('e.csv', b'\xff')])
        result = self.run_batch()
        self.assertEqual([m['status'] for m in result['members']], ['ok', 'partial', 'error', 'unsupported', 'error'])
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['member_conservation'], {'total': 5, 'ok': 1, 'partial': 1, 'error': 2, 'unsupported': 1})
        self.assertEqual(result['members'][1]['receipt']['row_conservation'].get('source_rows', 0), 0)

    def test_late_member_failure_rolls_back_rows_and_receipts_then_continues(self):
        from dataclasses import replace
        from unittest.mock import patch

        header, detail = statement(net='99', transaction='failed').splitlines(keepends=True)
        # Put invalid UTF-8 beyond both the delimiter sample and the text buffer,
        # so this exercises a failure after financial detail has been processed.
        cases = [('utf8', (header + detail * 256).encode() + b'\xff\n', {}),
                 ('logical-record', (header + detail + 'x' * 1025 + '\n').encode(),
                  {'max_record_chars': 1024})]
        for name, failed_member, limits in cases:
            with self.subTest(failure=name):
                self.output = self.root / name
                with zipfile.ZipFile(self.source, 'w', compression=zipfile.ZIP_STORED) as archive:
                    archive.writestr('a-before.csv', statement(transaction='before'))
                    archive.writestr('b-failed.csv', failed_member)
                    archive.writestr('c-after.csv', statement(net='0.0098', transaction='after'))
                profile = normalizer.PROFILES['distributor']
                normalize = normalizer.normalize
                processed = []
                snapshots = []

                def observe_detail(raw, source_row, source_label):
                    result = profile.normalize(raw, source_row, source_label)
                    if source_label.endswith('!/b-failed.csv'):
                        processed.append(result['owner_net_amount'])
                    return result

                def observe_member(provider, source, ledger, **options):
                    if not options['source_label'].endswith('!/b-failed.csv'):
                        return normalize(provider, source, ledger, **options)
                    before = ledger.read_bytes()
                    receipt_files = {str(p.relative_to(ledger.parent)): p.read_bytes()
                                     for p in ledger.parent.rglob('*') if p.is_file() and p != ledger}
                    try:
                        return normalize(provider, source, ledger, **options)
                    except (ValueError, UnicodeError, csv.Error):
                        self.assertEqual(ledger.read_bytes(), before)
                        after_files = {str(p.relative_to(ledger.parent)): p.read_bytes()
                                       for p in ledger.parent.rglob('*') if p.is_file() and p != ledger}
                        self.assertEqual(after_files, receipt_files)
                        snapshots.append(before)
                        raise

                with patch.dict(normalizer.PROFILES, {'distributor': replace(profile, normalize=observe_detail)}), \
                        patch.object(normalizer, 'normalize', side_effect=observe_member):
                    result = self.run_batch(**limits)
                self.assertGreater(len(processed), 0, 'Failure must occur after valid financial rows')
                self.assertEqual(set(processed), {'99'})
                self.assertEqual(len(snapshots), 1)
                self.assertEqual(result['status'], 'partial')
                self.assertEqual([(m['member'], m['status']) for m in result['members']],
                                 [('a-before.csv', 'ok'), ('b-failed.csv', 'error'), ('c-after.csv', 'ok')])
                self.assertEqual(result['member_conservation'], {'total': 3, 'ok': 2, 'error': 1})
                self.assertNotIn('receipt', result['members'][1])
                ledger_bytes = (self.output / 'ledger.csv').read_bytes()
                self.assertTrue(ledger_bytes.startswith(snapshots[0]))
                rows = list(csv.DictReader(io.StringIO(ledger_bytes.decode())))
                self.assertEqual([r['owner_net_amount'] for r in rows], ['0.0049', '0.0098'])
                self.assertEqual([r['source_file'] for r in rows],
                                 [f"zip:{result['archive_version_id']}!/{member}" for member in ['a-before.csv', 'c-after.csv']])
                self.assertEqual(sorted(p.name for p in (self.output / 'receipts').iterdir()),
                                 ['0001.json', '0001.rows.jsonl', '0003.json', '0003.rows.jsonl'])
                self.assertFalse((self.output / 'ledger.csv.receipts').exists())
                for index, row in zip([0, 2], rows):
                    receipt = result['members'][index]['receipt']
                    records = [json.loads(line) for line in (self.output / receipt['row_receipt']).read_text().splitlines()]
                    self.assertEqual(len(records), 1)
                    self.assertEqual(records[0]['ledger_line_id'], row['ledger_line_id'])
                    self.assertEqual(records[0]['disposition'], 'detail')

    def test_traversal_duplicate_symlink_and_encrypted_fail_before_output(self):
        for name in ['../bad.csv', '/bad.csv', 'a/../bad.csv', 'C:/bad.csv', 'a\\bad.csv']:
            with self.subTest(name=name):
                self.archive([(name, statement())])
                with self.assertRaises(ValueError): self.run_batch()
                self.assertFalse(self.output.exists())
        self.archive([('A.csv', statement()), ('a.csv', statement())])
        with self.assertRaises(ValueError): self.run_batch()
        info = zipfile.ZipInfo('link.csv'); info.create_system=3; info.external_attr=(stat.S_IFLNK | 0o777)<<16
        self.archive([(info, 'elsewhere')])
        with self.assertRaises(ValueError): self.run_batch()
        self.assertFalse(self.output.exists())

    def test_limits_prevent_publication(self):
        for limits in [{'max_members': 1}, {'max_expanded_bytes': 10}, {'max_member_bytes': 10}, {'max_ratio': 1}, {'max_archive_bytes': 10}, {'max_directory_bytes': 10}]:
            with self.subTest(limits=limits):
                self.archive([('a.csv', statement()), ('b.csv', statement())])
                with self.assertRaises(ValueError): self.run_batch(**limits)
                self.assertFalse(self.output.exists())

    def test_existing_output_and_corrupt_archive_never_replace_evidence(self):
        self.output.mkdir(); marker=self.output/'keep'; marker.write_text('keep')
        self.archive([('a.csv', statement())])
        with self.assertRaises(ValueError): self.run_batch()
        self.assertEqual(marker.read_text(), 'keep')
        marker.unlink(); self.output.rmdir()
        self.source.write_bytes(b'not zip')
        with self.assertRaises(ValueError): self.run_batch()
        self.assertFalse(self.output.exists())

    def test_corrupt_crc_and_encrypted_member_abort_entire_bundle(self):
        import struct
        self.archive([('a.csv', statement())])
        original = self.source.read_bytes()
        for corruption in ['crc', 'encrypted', 'count']:
            data = bytearray(original)
            central = data.index(b'PK\x01\x02')
            if corruption == 'crc':
                struct.pack_into('<L', data, central + 16, 123)
            elif corruption == 'encrypted':
                flags = struct.unpack_from('<H', data, central + 8)[0]
                struct.pack_into('<H', data, central + 8, flags | 1)
            else:
                end = data.rindex(b'PK\x05\x06')
                struct.pack_into('<HH', data, end + 8, 1, 2)
            self.source.write_bytes(data)
            with self.assertRaises((ValueError, zipfile.BadZipFile)):
                self.run_batch()
            self.assertFalse(self.output.exists())

    def test_zip64_locator_cannot_override_bounded_legacy_directory(self):
        import struct
        from _royalty_archive import DEFAULT_LIMITS, preflight_directory
        self.archive([('a.csv', statement())])
        data = self.source.read_bytes()
        end = list(struct.unpack('<4s4H2LH', data[-22:]))
        end[5] += 76
        zip64 = struct.pack('<4sQ2H2L4Q', b'PK\x06\x06', 44, 45, 45, 0, 0, 1, 1, 10*1024*1024, end[6])
        locator = struct.pack('<4sLQL', b'PK\x06\x07', 0, len(data)-22, 1)
        malicious = data[:-22]+zip64+locator+struct.pack('<4s4H2LH', *end)
        with self.assertRaisesRegex(ValueError, 'ZIP64'):
            preflight_directory(io.BytesIO(malicious), DEFAULT_LIMITS)

    def test_missing_fields_remain_held_and_tsv_uses_existing_detection(self):
        self.archive([('a.tsv', statement(currency='').replace(',', '\t'))])
        result = self.run_batch()
        self.assertEqual(result['status'], 'partial')
        with (self.output / 'ledger.csv').open() as stream: row=next(csv.DictReader(stream))
        self.assertEqual(row['currency'], '')
        self.assertIn('missing:currency', row['held_reasons'])

    def test_same_archive_replay_to_new_bundle_is_deterministic(self):
        self.archive([('b.csv', statement(transaction='two')), ('a.csv', statement())])
        self.run_batch()
        first = (self.output / 'ledger.csv').read_bytes()
        self.output = self.root / 'second'
        self.run_batch()
        self.assertEqual(first, (self.output / 'ledger.csv').read_bytes())

    def test_record_budget_and_column_limit_cover_headers_and_multiline(self):
        cases = [('wide-header', ','.join('h'+str(i) for i in range(1100))+'\n', {}),
                 ('wide-row', 'Title\n'+','*1100+'\n', {}),
                 ('large-record', 'Title\n'+','*(1024*1024+1)+'\n', {}),
                 ('multiline-record', 'Title\n"'+('x\n'*60)+'"\n', {'max_record_chars': 100})]
        for name, content, limits in cases:
            with self.subTest(name=name):
                self.output = self.root/name
                with zipfile.ZipFile(self.source, 'w', compression=zipfile.ZIP_STORED) as archive:
                    archive.writestr('a.csv', content)
                    archive.writestr('b.csv', statement())
                result = self.run_batch(**limits)
                self.assertEqual(result['members'][0]['status'], 'error')
                self.assertRegex(result['members'][0]['reason'], 'record|column')
                self.assertEqual(result['status'], 'partial')

    def test_cli_from_foreign_directory_and_vendored_copy(self):
        import subprocess
        self.archive([('a.csv', statement())])
        paths = [SCRIPTS/'normalize-royalty-statement.py',
                 SCRIPTS.parents[1]/'recoup-catalog-reconcile-royalties/scripts/normalize-royalty-statement.py']
        for index, path in enumerate(paths):
            output = self.root/f'bundle-{index}'
            result = subprocess.run([sys.executable, str(path), '--archive', '--provider', 'distributor',
                                     '--input', str(self.source), '--output', str(output)], cwd=self.root,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'ok')
            again = subprocess.run([sys.executable, str(path), '--archive', '--provider', 'distributor',
                                    '--input', str(self.source), '--output', str(output)], cwd=self.root,
                                   capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertIn('new bundle directory', again.stderr)

    def test_empty_and_directory_only_archives_are_not_success(self):
        for members in [[], [('folder/', '')]]:
            self.archive(members)
            with self.assertRaises(ValueError): self.run_batch()
            self.assertFalse(self.output.exists())

if __name__ == '__main__': unittest.main()

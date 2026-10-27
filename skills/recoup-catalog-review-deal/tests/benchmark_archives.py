#!/usr/bin/env python3
"""Synthetic ZIP resource measurement; no customer data or external services."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import resource
import sys
import tempfile
import time
import zipfile
from decimal import Decimal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', type=int, default=2000000)
    parser.add_argument('--members', type=int, default=2)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.members <= args.rows:
        parser.error('Require 1 <= members <= rows')
    scripts = Path(__file__).resolve().parents[1] / 'scripts'
    sys.path.insert(0, str(scripts))
    names = ['normalize-royalty-statement.py', '_royalty_archive.py', '_finance.py']
    hashes = {name: hashlib.sha256((scripts/name).read_bytes()).hexdigest() for name in names}
    import _royalty_archive  # Freeze the lazy helper before measurement.
    spec = importlib.util.spec_from_file_location('archive_benchmark', scripts / 'normalize-royalty-statement.py')
    subject = importlib.util.module_from_spec(spec); sys.modules[spec.name] = subject; spec.loader.exec_module(subject)
    with tempfile.TemporaryDirectory(prefix='synthetic-archive-benchmark-') as temporary:
        root = Path(temporary); source=root/'statements.zip'
        with zipfile.ZipFile(source, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for member in range(args.members):
                with archive.open(f'{member:04d}.csv', 'w') as binary:
                    with io.TextIOWrapper(binary, encoding='utf-8', newline='') as stream:
                        writer=csv.writer(stream)
                        writer.writerow(['Title','Period Start','Period End','Currency','Net','Rights Type','Income Type'])
                        for i in range(member, args.rows, args.members):
                            writer.writerow([f'Synthetic {i}','2024-01-01','2024-03-31','USD','.0049','publishing','performance'])
        started=time.monotonic()
        result=subject.normalize_archive('distributor', source, root/'output')
        elapsed=time.monotonic()-started
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rows=sum(m['receipt']['rows'] for m in result['members'])
        total=sum((Decimal(t['amount']) for m in result['members'] for t in m['receipt']['written_totals'] if t['field']=='owner_net_amount' and t['currency']=='USD'), Decimal(0))
        expected=Decimal('.0049')*args.rows
        assert result['status']=='ok' and rows==args.rows and total==expected
        after = {name: hashlib.sha256((scripts/name).read_bytes()).hexdigest() for name in names}
        assert hashes == after, 'Measured source changed during benchmark; discard this run'
        report=dict(synthetic=True, rows=rows, members=args.members, seconds=round(elapsed,3),
                    peak_rss_bytes=rss if sys.platform=='darwin' else rss*1024,
                    compressed_bytes=source.stat().st_size, expanded_bytes=result['expanded_bytes'],
                    output_bytes=sum(p.stat().st_size for p in (root/'output').rglob('*') if p.is_file()),
                    expected_usd=str(expected), observed_usd=str(total),
                    member_receipts=[m['receipt']['row_conservation'] for m in result['members']],
                    source_hashes=hashes,
                    python=sys.version.split()[0], platform=sys.platform,
                    limitation='Synthetic uniform rows; repeated append scans prior ledger per member. Output and temporary disk scale with rows; no provider or hosted proof.')
        Path(args.output).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()

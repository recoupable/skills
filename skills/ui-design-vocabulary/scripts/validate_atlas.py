#!/usr/bin/env python3
"""Verify that every declared atlas state has its captured, current-source image."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    capture = json.loads((ASSETS / 'capture-record.json').read_text())
    errors = []
    expected = {f"{c['id']}-{n}.jpg" for c in manifest['cards'] for n in range(len(c['states']))}
    actual = {p.name for p in (ASSETS / 'screenshots').glob('*.jpg')}
    if actual != expected:
        errors.append(f'Screenshot coverage mismatch: missing={expected-actual}, extra={actual-expected}')
    if len({c['id'] for c in manifest['cards']}) != len(manifest['cards']):
        errors.append('Duplicate card IDs')
    index = (ROOT / 'references/visual-index.md').read_text()
    for name in sorted(expected):
        path = ASSETS / 'screenshots' / name
        if name not in index:
            errors.append(f'Unindexed screenshot: {name}')
        if not path.exists():
            continue
        data = path.read_bytes()
        if not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
            errors.append(f'Invalid JPEG envelope: {name}')
        if capture['screenshots'].get(name) != sha(path):
            errors.append(f'Changed or uncatalogued screenshot: {name}')
    for name, digest in capture['sources'].items():
        if sha(ASSETS / name) != digest:
            errors.append(f'Source changed since capture: {name}; recapture affected states')
    data_text = (ASSETS / 'atlas-data.js').read_text()
    cards = json.loads(data_text.removeprefix('window.ATLAS = ').rstrip().removesuffix(';'))
    if cards != manifest['cards']:
        errors.append('Renderer data and manifest differ')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f"Atlas integrity passed: {len(manifest['cards'])} cards, {len(expected)} screenshots, all indexed and source hashes current.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

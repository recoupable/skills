"""Bounded artifact readers; no import, source normalization or financial logic."""
import csv
import hashlib
from pathlib import Path
from _royalty_archive import BoundedCsvLines

MAX_JSON_BYTES = 1024 * 1024
MAX_ROW_RECEIPT_BYTES = 16 * 1024 * 1024
MAX_JSONL_RECORD_BYTES = 256 * 1024
MAX_CURRENT_ROWS = 10000
MAX_LEDGER_BYTES = 256 * 1024 * 1024
MAX_LEDGER_ROWS = 1000000
MAX_CSV_RECORD_CHARS = 256 * 1024
MAX_FIELD_CHARS = 65536
MAX_REASONS = 64
CHUNK = 1024 * 1024


def admit(path, limit):
    if Path(path).stat().st_size > limit:
        raise ValueError('Artifact exceeds supported byte limit')


def read_small(path):
    admit(path, MAX_JSON_BYTES)
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError('JSON exceeds supported byte limit')
    return raw


def copy_hash(path, target=None):
    """Hash a bounded stream, optionally preserving identical bytes in a snapshot."""
    admit(path, MAX_LEDGER_BYTES)
    digest, size = hashlib.sha256(), 0
    with Path(path).open('rb') as stream:
        while block := stream.read(min(CHUNK, MAX_LEDGER_BYTES - size + 1)):
            size += len(block)
            if size > MAX_LEDGER_BYTES:
                raise ValueError('Artifact exceeds supported byte limit')
            digest.update(block)
            if target is not None: target.write(block)
    return digest.hexdigest()


def bounded_shape(value):
    """Cap decoded per-record fields, nesting and reasons before retaining it."""
    stack, nodes = [(value, 0)], 0
    while stack:
        item, depth = stack.pop(); nodes += 1
        if depth > 16 or nodes > 4096:
            raise ValueError('Row receipt structure exceeds supported bounds')
        if isinstance(item, str) and len(item) > MAX_FIELD_CHARS:
            raise ValueError('Row receipt field exceeds supported limit')
        if isinstance(item, dict):
            if len(item) > 256: raise ValueError('Too many row receipt fields')
            stack.extend((v, depth + 1) for pair in item.items() for v in pair)
        elif isinstance(item, list):
            if len(item) > 2048: raise ValueError('Row receipt list exceeds supported limit')
            stack.extend((v, depth + 1) for v in item)


def read_rows(path, parse):
    admit(path, MAX_ROW_RECEIPT_BYTES)
    rows, size, digest = [], 0, hashlib.sha256()
    with Path(path).open('rb') as stream:
        while line := stream.readline(MAX_JSONL_RECORD_BYTES + 1):
            size += len(line)
            if len(line) > MAX_JSONL_RECORD_BYTES or size > MAX_ROW_RECEIPT_BYTES:
                raise ValueError('Row receipt exceeds supported byte limits')
            digest.update(line)
            if not line.strip(): continue
            if len(rows) >= MAX_CURRENT_ROWS:
                raise ValueError('Too many current import rows')
            row = parse(line)
            if not isinstance(row, dict) or not isinstance(row.get('reasons'), list) or len(row['reasons']) > MAX_REASONS:
                raise ValueError('Unsupported row reasons')
            # Source CSV column count is not a projected-object shape constraint.
            # Keep wire-byte and individual private field bounds, then discard raw columns.
            raw = row.pop('raw_values', None)
            if isinstance(raw, dict):
                for key, value in raw.items():
                    bounded_shape(key); bounded_shape(value)
            else:
                bounded_shape(raw)
            bounded_shape(row)
            rows.append({key: row[key] for key in ('source_version_id', 'source_sheet', 'source_row', 'disposition', 'reasons', 'ledger_line_id')})
    return rows, digest.hexdigest()


def ledger_rows(path, columns):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        lines = BoundedCsvLines(stream, MAX_CSV_RECORD_CHARS)
        reader = csv.DictReader(lines)
        if reader.fieldnames != columns:
            raise ValueError('Unsupported ledger schema')
        lines.reset()
        for number, row in enumerate(reader, 1):
            if number > MAX_LEDGER_ROWS or None in row or any(v is None or len(v) > MAX_FIELD_CHARS for v in row.values()):
                raise ValueError('Ledger record exceeds supported shape or bounds')
            yield row
            lines.reset()

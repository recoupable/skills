"""Bounded ZIP batches for the existing royalty normalizer; never extract member paths."""
from collections import Counter
import csv
import hashlib
import json
import re
from pathlib import Path
import shutil
import stat
import struct
import tempfile
import unicodedata
import zipfile

CHUNK = 1024 * 1024
DEFAULT_LIMITS = dict(max_members=128, max_archive_bytes=256 * CHUNK,
                      max_directory_bytes=CHUNK, max_member_bytes=512 * CHUNK,
                      max_expanded_bytes=1024 * CHUNK, max_ratio=200,
                      max_record_chars=CHUNK, max_columns=1024,
                      max_controls_bytes=CHUNK, max_controls_entries=128)


class BoundedCsvLines:
    """Budget characters before csv can allocate an unbounded logical record.

    A character uses at most four UTF-8 bytes. Reset only after csv yields a whole
    logical record, not each physical line, so quoted newlines cannot evade it.
    """
    def __init__(self, stream, limit):
        self.stream = stream
        self.limit = limit
        self.reset()

    def reset(self):
        self.remaining = self.limit

    def __iter__(self):
        return self

    def __next__(self):
        line = self.stream.readline(self.remaining + 1)
        if not line:
            raise StopIteration
        self.remaining -= len(line)
        if self.remaining < 0:
            raise ValueError('CSV logical record character limit exceeded')
        return line


def copy_bounded(source, target, limit):
    digest = hashlib.sha256(); size = 0
    while block := source.read(min(CHUNK, limit - size + 1)):
        size += len(block)
        if size > limit:
            raise ValueError('Archive byte limit exceeded')
        target.write(block); digest.update(block)
    return size, digest.hexdigest()


def preflight_directory(stream, limits):
    """Bound central-directory allocation before ZipFile constructs its member list."""
    stream.seek(0, 2); size = stream.tell()
    stream.seek(max(0, size - 65557)); tail = stream.read(65557)
    pos = tail.rfind(b'PK\x05\x06')
    if pos < 0 or len(tail) - pos < 22:
        raise ValueError('Missing ZIP end record')
    _, disk, directory_disk, disk_count, count, directory_size, offset, comment = struct.unpack('<4s4H2LH', tail[pos:pos+22])
    if pos + 22 + comment != len(tail) or disk or directory_disk or disk_count != count:
        raise ValueError('Split or malformed ZIP is unsupported')
    end_offset = size - len(tail) + pos
    if end_offset >= 20:
        stream.seek(end_offset - 20)
        if stream.read(4) == b'PK\x06\x07':
            raise ValueError('ZIP64 locator is unsupported')
    if count == 65535 or directory_size == 0xffffffff or offset == 0xffffffff:
        raise ValueError('ZIP64 is unsupported; split into bounded standard ZIP batches')
    if not count or count > limits['max_members'] or directory_size > limits['max_directory_bytes']:
        raise ValueError('Archive member or directory limit exceeded')
    if offset + directory_size != size - len(tail) + pos:
        raise ValueError('Unexpected ZIP directory layout')
    stream.seek(0)
    return count


def members_checked(archive, limits, expected_count):
    infos = archive.infolist()
    if len(infos) != expected_count or len(infos) > limits['max_members']:
        raise ValueError('ZIP member count mismatch')
    names = set(); total = 0; result = []
    for info in infos:
        name = info.orig_filename
        normalized = unicodedata.normalize('NFC', name.rstrip('/')).casefold()
        parts = name.rstrip('/').split('/')
        mode = info.external_attr >> 16
        if (not name or info.filename != name or '\\' in name or ':' in name
                or any(ord(c) < 32 or ord(c) == 127 for c in name)
                or any(p in {'', '.', '..'} for p in parts) or normalized in names):
            raise ValueError('Unsafe or duplicate archive member name')
        names.add(normalized)
        if stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}:
            raise ValueError('Links and special archive members are unsupported')
        if info.flag_bits & 1 or info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
            raise ValueError('Encrypted or unsupported compression method')
        if info.is_dir():
            if info.file_size or info.compress_size:
                # Deflated empty directories have a nonzero compressed representation.
                if info.file_size:
                    raise ValueError('Directory member has data')
            continue
        if stat.S_ISDIR(mode):
            raise ValueError('Inconsistent directory member')
        total += info.file_size
        if (info.file_size > limits['max_member_bytes'] or total > limits['max_expanded_bytes']
                or info.file_size > max(info.compress_size, 1) * limits['max_ratio']):
            raise ValueError('Archive expanded size or compression ratio limit exceeded')
        result.append(info)
    if not result:
        raise ValueError('Archive contains no files')
    return sorted(result, key=lambda info: info.filename)


def load_controls_manifest(path, archive_hash, names, limits):
    """Read once with a byte budget; bind controls without filename inference."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate controls manifest JSON key')
            result[key] = value
        return result

    with Path(path).open('rb') as stream:
        raw = stream.read(limits['max_controls_bytes'] + 1)
    if len(raw) > limits['max_controls_bytes']:
        raise ValueError('Controls manifest byte limit exceeded')
    try:
        manifest = json.loads(raw, parse_float=str, object_pairs_hook=unique_object,
                              parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite manifest number')))
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('Invalid controls manifest encoding or nesting') from exc
    if (not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int
            or manifest['schema_version'] != 1
            or set(manifest) - {'schema_version', 'archive_version_id', 'members'}):
        raise ValueError('Invalid controls manifest schema')
    if 'archive_version_id' in manifest and manifest['archive_version_id'] != archive_hash:
        raise ValueError('Controls manifest archive hash mismatch')
    members = manifest.get('members')
    if not isinstance(members, list) or len(members) > limits['max_controls_entries']:
        raise ValueError('Controls manifest entries must be a bounded list')
    bindings = {}
    for entry in members:
        if not isinstance(entry, dict) or set(entry) != {'member', 'source_version_id', 'controls'}:
            raise ValueError('Controls binding requires exact member, source_version_id and controls')
        name = entry['member']; digest = entry['source_version_id']
        if not isinstance(name, str) or name not in names:
            raise ValueError('Unknown controls manifest member')
        if name in bindings:
            raise ValueError('Duplicate controls manifest member')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('Controls binding requires lowercase member SHA256')
        bindings[name] = entry
    return raw, bindings


def normalize_zip(normalize, provider, input_path, output_path, *, delimiter='auto',
                  column_map_path=None, statement_id=None, archive_controls_path=None, **overrides):
    limits = {**DEFAULT_LIMITS, **overrides}
    if set(limits) != set(DEFAULT_LIMITS) or any(type(v) is not int or v <= 0 for v in limits.values()):
        raise ValueError('Archive limits must be positive integers with known names')
    input_path = Path(input_path); output_path = Path(output_path)
    if output_path.exists() or output_path.is_symlink():
        raise ValueError('Archive output must be a new bundle directory')
    if not input_path.is_file() or input_path.stat().st_size > limits['max_archive_bytes']:
        raise ValueError('Archive is not a bounded regular file')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Disk snapshot binds the hash to the bytes parsed, even if the source later changes.
    with tempfile.TemporaryDirectory(prefix='royalty-batch-', dir=output_path.parent) as tmp:
        tmp = Path(tmp); snapshot = tmp / 'archive.zip'; bundle = tmp / 'bundle'; bundle.mkdir()
        with input_path.open('rb') as source, snapshot.open('wb') as target:
            archive_bytes, archive_hash = copy_bounded(source, target, limits['max_archive_bytes'])
        entries = []; expanded = 0; controls_hash = None; bindings = {}
        with snapshot.open('rb') as stream:
            expected_count = preflight_directory(stream, limits)
            with zipfile.ZipFile(stream) as archive:
                infos = members_checked(archive, limits, expected_count)
                if archive_controls_path is not None:
                    raw, bindings = load_controls_manifest(archive_controls_path, archive_hash,
                                                           {info.filename for info in infos}, limits)
                    controls_hash = hashlib.sha256(raw).hexdigest()
                    (bundle / 'controls-manifest.json').write_bytes(raw)
                for index, info in enumerate(infos, 1):
                    member_path = tmp / ('member' + Path(info.filename).suffix.lower())
                    with archive.open(info) as source, member_path.open('wb') as target:
                        size, member_hash = copy_bounded(source, target, min(limits['max_member_bytes'], limits['max_expanded_bytes'] - expanded))
                    expanded += size
                    if size != info.file_size or size > max(info.compress_size, 1) * limits['max_ratio']:
                        raise ValueError('Expanded member differs from bounded metadata')
                    entry = dict(member=info.filename, source_version_id=member_hash, bytes=size)
                    binding = bindings.get(info.filename)
                    if binding is not None and binding['source_version_id'] != member_hash:
                        entry.update(status='error', reason='Controls binding member hash mismatch')
                    elif member_path.suffix not in {'.csv', '.tsv'}:
                        entry.update(status='unsupported', reason='Only UTF-8 CSV/TSV members are supported; no nested archives or spreadsheets')
                    else:
                        controls_path = None
                        if binding is not None:
                            controls_path = tmp / 'member-controls.json'
                            controls_path.write_text(json.dumps(binding['controls']))
                        try:
                            receipt = normalize(provider, member_path, bundle / 'ledger.csv',
                                                delimiter=delimiter, column_map_path=column_map_path,
                                                append=True, statement_id=statement_id, controls_path=controls_path,
                                                source_label=f'zip:{archive_hash}!/{info.filename}',
                                                csv_limits=(limits['max_record_chars'], limits['max_columns']))
                        except (ValueError, UnicodeError, csv.Error, OverflowError) as exc:
                            entry.update(status='error', reason=str(exc))
                        else:
                            # Bundle-relative receipt paths survive the atomic directory publication.
                            if binding is not None:
                                receipt['archive_controls_version_id'] = controls_hash
                            old_receipt = Path(receipt['receipt'])
                            old_rows = Path(receipt['row_receipt'])
                            relative = f'receipts/{index:04d}'
                            (bundle / 'receipts').mkdir(exist_ok=True)
                            receipt.update(archive_version_id=archive_hash, archive_member=info.filename,
                                           output='ledger.csv', receipt=relative+'.json', row_receipt=relative+'.rows.jsonl')
                            old_rows.rename(bundle / receipt['row_receipt']); old_receipt.unlink()
                            (bundle / receipt['receipt']).write_text(json.dumps(receipt, indent=2)+'\n')
                            entry.update(status=receipt['status'], receipt=receipt)
                    member_path.unlink(); entries.append(entry)
        shutil.rmtree(bundle / 'ledger.csv.receipts', ignore_errors=True)
        counts = Counter(e['status'] for e in entries)
        payload = dict(status='ok' if counts['ok'] == len(entries) else 'partial',
                       batch_version='royalty-zip/1', archive_input=str(input_path.resolve()),
                       archive_version_id=archive_hash, archive_bytes=archive_bytes,
                       expanded_bytes=expanded, limits=limits, ordering='Exact member name, ascending Unicode order; not statement chronology',
                       member_conservation={'total': len(entries), **dict(counts)},
                       members=entries, output=str(output_path),
                       overlap_detection='Existing normalizer only: exact member bytes and scoped transaction keys. Unkeyed overlap requires manual review.',
                       controls_status='unavailable: no independent source controls supplied; use --archive-controls for member bindings')
        if archive_controls_path is not None:
            payload.update(controls_status='per-member: see individual receipts; no aggregate control conclusion',
                           archive_controls_version_id=controls_hash, controls_manifest='controls-manifest.json')
        (bundle / 'manifest.json').write_text(json.dumps(payload, indent=2)+'\n')
        if output_path.exists() or output_path.is_symlink():
            raise ValueError('Archive output appeared during processing; refusing replacement')
        bundle.rename(output_path)
    return payload

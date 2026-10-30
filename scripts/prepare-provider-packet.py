#!/usr/bin/env python3
"""Prepare a local profile-bound evidence packet; never authorize or submit."""
import argparse
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('catalog_case', HERE / 'catalog-case.py')
case_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case_api)
require = case_api.require
fingerprint = case_api.fingerprint
field_spec = importlib.util.spec_from_file_location('mlc_fields', HERE / 'mlc-public-fields.py')
field_api = importlib.util.module_from_spec(field_spec)
field_spec.loader.exec_module(field_api)


def bounded_bytes(path, limit):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, 'Input exceeds preparation size limit')
    return data


def strict_json(raw, *, exact_floats=False):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    def decimal_float(token):
        message = 'Numeric precision would be lost; supply high-precision decimals as quoted strings'
        value = float(token)
        try:
            exact = Decimal(token)
            decoded = Decimal(str(value))
            require(exact == decoded, message)
            require(decoded.is_finite(), 'Nonfinite JSON number')
        except InvalidOperation:
            raise ValueError(message) from None
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_float=decimal_float if exact_floats else float,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))


def prepare(case_path, mapping_path, output_path):
    output_path = Path(output_path)
    require(not output_path.exists() and not output_path.is_symlink(), 'Output must be a new file')
    case_raw = bounded_bytes(case_path, 16 * 1024 * 1024)
    # Use the existing case reader and require an unchanged byte snapshot around it.
    strict_json(case_raw)
    case = case_api.read_case(case_path)
    require(bounded_bytes(case_path, 16 * 1024 * 1024) == case_raw, 'Case changed while reading')
    mapping_raw = bounded_bytes(mapping_path, 1024 * 1024)
    mapping = strict_json(mapping_raw, exact_floats=True)
    fields = {'case_id', 'revision', 'action_id', 'payload_sha256', 'profile_id',
              'profile_version', 'role', 'required_inputs'}
    require(isinstance(mapping, dict) and set(mapping) in (fields, fields | {'field_values'}), 'Mapping requires exact binding and evidence fields')
    require(isinstance(case.get('case_id'), str) and case['case_id'].strip(), 'Missing case ID')
    require(type(case['revision']) is int and case['revision'] >= 0, 'Invalid case revision')
    require(mapping['case_id'] == case['case_id'] and type(mapping['revision']) is int
            and mapping['revision'] == case['revision'], 'Case/revision binding mismatch')
    require(mapping['profile_id'] == 'mlc-new-work', 'Only sourced mlc-new-work preparation is implemented')
    references = HERE.parent / 'references' / 'catalog-providers'
    registry_raw = bounded_bytes(references / 'operations.json', 1024 * 1024)
    sources_raw = bounded_bytes(references / 'sources.json', 1024 * 1024)
    registry = strict_json(registry_raw); sources = strict_json(sources_raw)
    profiles = [p for p in registry['operations'] if p['profile_id'] == mapping['profile_id']]
    require(len(profiles) == 1, 'Profile must resolve uniquely')
    profile = profiles[0]
    require(mapping['profile_version'] == profile['profile_version'], 'Profile version mismatch')
    require(profile['capability']['preparation'] == 'evidence_packet'
            and profile['documented_route'] == 'member_portal_or_eligible_cwr', 'Unverified or unsupported preparation route')
    source_index = {s['id']: s for s in sources['sources']}
    profile_sources = [source_index[sid] for sid in profile['source_ids']]
    require(profile_sources and all(s['check_result'] == 'verified' for s in profile_sources),
            'Profile contains unverified source placeholders')
    action = case['actions'].get(mapping['action_id'])
    require(action and action.get('status') in {'prepared', 'authorized'}
            and not action.get('stale') and not action.get('withheld'), 'Action is stale, withdrawn or unavailable')
    require(action['id'] == mapping['action_id'], 'Action key/ID mismatch')
    payload = action['payload']
    require(mapping['payload_sha256'] == fingerprint(payload), 'Payload binding mismatch')
    require(action['stage'] == profile['stage'] and payload['provider'] == profile['provider']
            and payload['operation'] == profile['operation'], 'Action stage/provider/operation mismatch')
    # These are explicit local scope fields, not invented provider-form fields.
    require(payload['scope'].get('subject_type') == profile['subject_type'], 'Action subject type mismatch or missing')
    rights = payload['scope'].get('rights')
    require(isinstance(rights, list) and rights and all(r in profile['rights'] for r in rights),
            'Action rights mismatch or missing')
    require(mapping['role'] in profile['eligible_roles'], 'Supplied role is not eligible for this profile')
    related_actions = {rid for rid, candidate in case['actions'].items()
                       if candidate.get('payload') == payload}
    require(not any(a.get('action_id') in related_actions for a in case['attempts'].values()),
            'Existing attempt: reconcile the case instead of preparing duplicate intake')
    require(not any(o.get('action_id') in related_actions for o in case['outcomes'].values()),
            'Existing outcome: resume the case instead of preparing duplicate intake')
    supplied = mapping['required_inputs']
    require(isinstance(supplied, dict) and not set(supplied) - set(profile['required_inputs']),
            'Unknown required-input label; use exact profile labels')
    # Validate the action and every referenced dependency with the existing contract.
    records = {}; groups = {}
    for group in case_api.COLLECTIONS:
        for rid, record in case[group].items():
            require(rid not in records and record.get('id') == rid, 'Invalid or duplicate record ID')
            records[rid] = record; groups[rid] = group
    checked = set()
    def validate(rid):
        require(rid in records, 'Missing evidence/dependency record')
        if rid in checked:
            return
        record = records[rid]
        require(not record.get('stale') and not record.get('withheld'), 'Stale or withheld evidence/dependency')
        if groups[rid] == 'sources':
            require(record['status'] == 'active', 'Withdrawn evidence')
        clean = copy.deepcopy(record)
        clean.pop('stale', None); clean.pop('stale_reasons', None)
        case_api.validate_record(case, groups[rid], clean)
        checked.add(rid)
        for dep in record.get('depends_on', []):
            validate(dep)
        for ref in record.get('source_refs', []):
            validate(ref['source_id'])
    validate(action['id'])
    evidence = []; missing = []
    for label in profile['required_inputs']:
        refs = supplied.get(label, [])
        require(isinstance(refs, list), 'Required-input evidence must be a list of source references')
        for ref in refs:
            require(isinstance(ref, dict) and set(ref) == {'source_id', 'version'}, 'Evidence requires source_id/version')
            source = case['sources'].get(ref['source_id'])
            require(source and source['version'] == ref['version'], 'Evidence version mismatch')
            validate(ref['source_id'])
        if not refs:
            missing.append(label)
        evidence.append({'required_input': label, 'status': 'supplied' if refs else 'missing',
                         'source_refs': refs, 'semantic_verification': 'unverified'})
    packet = {'packet_version': 'catalog-preparation/1', 'status': 'blocked' if missing else 'prepared',
              'validation_scope': 'Local bindings and evidence structure only; not a provider form or CWR file',
              'external_preflight': 'unverified', 'case_id': case['case_id'], 'workspace_id': case['workspace_id'],
              'case_revision': case['revision'], 'case_sha256': hashlib.sha256(case_raw).hexdigest(),
              'action_id': action['id'], 'action_sha256': fingerprint(action),
              'action_status': action['status'], 'payload': payload,
              'payload_sha256': fingerprint(payload), 'mapping_sha256': hashlib.sha256(mapping_raw).hexdigest(),
              'profile_id': profile['profile_id'], 'profile_version': profile['profile_version'],
              'profile_sha256': fingerprint(profile), 'profile': profile,
              'profile_sources': profile_sources, 'profile_checked_at': registry['checked_at'],
              'sources_checked_at': sources['checked_at'], 'supplied_role': mapping['role'],
              'role_verification': 'unverified', 'required_inputs': evidence, 'missing_inputs': missing,
              'evidence_sources': {rid: case['sources'][rid] for rid in sorted(checked) if groups[rid] == 'sources'},
              'human_steps': profile['preflight'] + [
                  'Inspect the current authorized provider form and map actual required fields; this packet is not filing-ready.',
                  'Verify current account role, mandate, territory, effective period, disclosure and costs before any operation.',
                  'Search existing case attempts and provider records before any separately authorized submission.',
                  'Record an actual submission receipt and provider readback separately only if execution later occurs.'],
              'authority_effect': 'None: preparation neither grants authority nor creates an attempt or receipt'}
    guidance = strict_json(bounded_bytes(references / 'mlc-public-preparation.json', 1024 * 1024))
    require(set(guidance['required_input_guidance']) == set(profile['required_inputs']),
            'Public guidance does not cover the current profile inputs')
    packet.update({
        'public_preparation_guidance': guidance,
        'public_preparation_guidance_sha256': fingerprint(guidance),
        'missing_input_guidance': {label: guidance['required_input_guidance'][label] for label in missing},
        'field_validation': 'not_performed',
        'template_retrieval': 'not_performed_by_helper',
    })
    if 'field_values' in mapping:
        checks = field_api.check_fields(mapping['field_values'], payload['subjects'])
        packet['public_field_checks'] = checks
        packet['field_validation'] = checks['status']
        if checks['status'] == 'needs_attention':
            packet['status'] = 'blocked'
    encoded = (json.dumps(packet, indent=2, allow_nan=False) + '\n').encode('utf-8')
    require(bounded_bytes(case_path, 16 * 1024 * 1024) == case_raw, 'Case changed during preparation')
    # Exclusive creation also rejects hard links, symlinks and a racing output writer.
    fd = os.open(output_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
    except BaseException:
        output_path.unlink()
        raise
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True)
    parser.add_argument('--mapping', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        result = prepare(args.case, args.mapping, args.output)
        print(json.dumps({'status': result['status'], 'output': args.output, 'missing_inputs': result['missing_inputs']}))
        return 0 if result['status'] == 'prepared' else 1
    except (ValueError, KeyError, OSError, TypeError, RecursionError) as exc:
        print(f'prepare-provider-packet: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

"""Check a documented subset of MLC individual-registration fields locally."""
from decimal import Decimal, InvalidOperation


def check_fields(values, subjects):
    """Preserve supplied values; never infer identities, shares, or authority."""
    allowed = {'subject_id', 'work_title', 'writers', 'collection_shares', 'recordings'}
    if not isinstance(values, dict) or set(values) - allowed:
        raise ValueError('Field values require known worksheet keys')
    if (not isinstance(subjects, list) or len(subjects) != 1
            or not isinstance(values.get('subject_id'), str)
            or values['subject_id'] != subjects[0]):
        raise ValueError('Field checks require one existing action subject with an exact subject_id')
    findings = []

    def issue(path, message):
        findings.append({'path': path, 'message': message})

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def rows(key, required):
        value = values.get(key)
        if value is None and not required:
            return []
        if not isinstance(value, list) or (required and not value):
            issue(key, 'Supply a nonempty list.' if required else 'Supply a list or omit optional recordings.')
            return []
        return value

    if not text(values.get('work_title')):
        issue('work_title', 'Supply the composition title from existing evidence.')
    writers = rows('writers', True)
    roles = {'AD', 'AR', 'A', 'C', 'CA', 'SR', 'SA', 'TR', 'PA'}
    for index, writer in enumerate(writers):
        path = f'writers[{index}]'
        if not isinstance(writer, dict) or set(writer) - {'name', 'role'}:
            issue(path, 'Writer entries accept name and role only.')
            continue
        if not text(writer.get('name')):
            issue(path + '.name', 'Supply the known writer name.')
        if not isinstance(writer.get('role'), str) or writer['role'] not in roles:
            issue(path + '.role', 'Use a documented writer role code.')
    if writers and not any(isinstance(w, dict) and w.get('role') in ('C', 'CA') for w in writers):
        issue('writers', 'A new registration needs at least one Composer (C) or Composer/Author (CA).')
    for index, share in enumerate(rows('collection_shares', True)):
        path = f'collection_shares[{index}]'
        if not isinstance(share, dict) or set(share) - {'party', 'percent'}:
            issue(path, 'Collection entries accept party and percent only.')
            continue
        if not text(share.get('party')):
            issue(path + '.party', 'Identify the collecting publisher or administrator.')
        value = share.get('percent')
        try:
            if type(value) not in (str, int, float):
                raise ValueError()
            number = Decimal(str(value))
            if not number.is_finite() or not Decimal('0.01') <= number <= Decimal('100'):
                raise ValueError()
        except (ValueError, InvalidOperation):
            issue(path + '.percent', 'Supply an evidenced collection percentage from 0.01 through 100.')
    for index, recording in enumerate(rows('recordings', False)):
        path = f'recordings[{index}]'
        if not isinstance(recording, dict) or set(recording) - {'title', 'artist'}:
            issue(path, 'Optional recording entries accept title and artist only.')
            continue
        for key in ('title', 'artist'):
            if not text(recording.get(key)):
                issue(path + '.' + key, 'A supplied recording needs both title and artist.')
    return {'status': 'needs_attention' if findings else 'checked_public_subset',
            'rules_version': 'mlc-individual-public-fields/1',
            'values': values, 'findings': findings,
            'authority_verification': 'unverified',
            'scope': 'Local worksheet checks only; not a complete provider schema or filing validation.'}

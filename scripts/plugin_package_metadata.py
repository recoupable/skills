"""Host-specific metadata and submission instructions for generated packages."""
import hashlib
import json
from plugin_openai_review import review_test_cases

def stamp_versions(value, version):
    if isinstance(value, dict):
        return {k: version if k == 'version' else stamp_versions(v, version) for k,v in value.items()}
    if isinstance(value, list):
        return [stamp_versions(v, version) for v in value]
    return value

def prepare_metadata(files, audience, version, chatgpt_app_id, workspace_name):
    customer = audience != "full"
    for name in files:
        if name.endswith(('plugin.json','marketplace.json')) and name.startswith(('.codex-plugin/', '.claude-plugin/', '.cursor-plugin/', '.agents/plugins/')):
            metadata = stamp_versions(json.loads(files[name]), version)
            if name.endswith('/plugin.json'):
                metadata['name'] = 'recoup-plugin'
            if 'author' in metadata:
                metadata['author'].update(email='agent@recoupable.dev', url='https://recoupable.dev')
            if 'homepage' in metadata:
                metadata['homepage'] = 'https://recoupable.dev'
            if 'interface' in metadata:
                metadata['interface']['displayName'] = 'Recoup'
                metadata['interface']['websiteURL'] = 'https://recoupable.dev'
            if name == '.codex-plugin/plugin.json':
                host = 'ChatGPT' if audience in {'customer', 'workspace'} else 'Codex'
                metadata.setdefault('interface', {})['shortDescription'] = f'A record label inside {host}'
                if customer:
                    icon = 'assets/recoup-customer-icon.png'
                    if icon not in files:
                        raise ValueError(f'Missing customer icon: {icon}')
                    metadata['interface']['logo'] = f'./{icon}'
                    metadata['interface']['composerIcon'] = f'./{icon}'
                    review = metadata.setdefault('extensions', {}).setdefault('com.openai', {}).setdefault('review', {})
                    review['commerce'] = False
                    review['commerce_description'] = (
                        'Uses features and credits already available to the connected Recoup account. '
                        'Does not initiate subscriptions, upgrades, card setup, credit purchases or '
                        'automatic credit purchases. If an entitlement is missing, preserves the '
                        'task and explains the limit without transactional links.'
                    )
                    if audience == 'customer':
                        review['test_cases'] = review_test_cases()
            if audience == 'workspace' and name == '.codex-plugin/plugin.json':
                metadata.pop('mcpServers', None)
                metadata['apps'] = './.app.json'
                if workspace_name:
                    metadata['name'] = workspace_name
            files[name] = (json.dumps(metadata,indent=2)+'\n').encode()
    if audience == 'workspace':
        del files['.mcp.json']
        files['.app.json'] = (json.dumps({'apps': {'recoup': {'id': chatgpt_app_id, 'required': True}}}, indent=2)+'\n').encode()

def write_handoff(out, version, commit, chatgpt_app_id):
    (out/'OPENAI-SUBMISSION.md').write_text(f'''# Recoup {version}

Source commit: {commit}

Upload `recoup-customer-{version}.zip` to the existing Recoup draft in the OpenAI
publisher dashboard. Do not upload the full staff package to the public directory.
Resolve scans, complete MCP/reviewer setup, submit for review, then publish after approval.
This GitHub release is not evidence of OpenAI approval or publication.

## Commerce remediation and submission order

Deploy the matching API commerce-boundary changes before uploading this package
or resubmitting. API-sourced credit deductions must not trigger auto-top-up;
research entitlement failures must not mint card-setup checkout sessions. Verify
the deployed revision, then refresh/rescan the hosted MCP tools. A ZIP upload
does not deploy the API. This applies to all customers, not only reviewers.

The packaged fan-connection and recovery instructions use existing entitlements
only. A missing entitlement preserves the task and stops without plan promotion,
transactional links or purchases. OAuth credentials stay with the host; the agent
must not collect API keys, passwords or email verification codes in conversation.
The generated OpenAI review metadata declares this boundary explicitly.

Use the existing rejected draft. Upload only the customer ZIP, retain the correct
registered MCP server, and inspect every scan finding before resubmitting. Enter
reviewer access privately in the dashboard, never in the ZIP or source control.
Provide an existing entitled demo account with sample data only. Use a sign-in
method accepted by the current publisher form: dedicated demo credentials or the
reviewer email supplied there for a supported email-code/magic-link flow. Keep
reviewer access private and verify that no account setup is left to the reviewer.
Do not change production roles or grant paid access as part of packaging.

## Review cases to verify in the actual host

These are acceptance cases, not a claim that live or paid execution has passed.
The customer ZIP declares exactly five positive and three negative cases for its
single registered MCP server; review their prompts and expected outcomes in the
publisher form. Local/workspace adapters do not overwrite those review cases. Record a
reviewer-accessible walkthrough after deployment and installed-package checks.

Positive cases cover workflow/roster discovery, saved release-pack context with
missing inputs, one original graphic within existing credits, an unpublished
site draft and accessible saved catalog records. The generation case requires
the dedicated demo account's existing credits and access; do not run it as part
of packaging or claim it passed from source/ZIP checks.

Negative cases cover purchase/upgrade requests, unauthorized workspace access
and credential export/login-code collection. Separately verify exhausted-credit
and missing-fan-entitlement recovery without starting a purchase or paid retry.

Do not resubmit until live evidence supports the declared behavior. OpenAI's
review decision remains separate from source checks and GitHub publication.
Guidelines: https://developers.openai.com/plugins/plugin-guidelines
Submission: https://developers.openai.com/plugins/deploy/submission

The full ZIP contains all staff and customer skills. Both packages come from this commit.
Checksums, per-file customer content digests, source provenance and complete skill inventories are in release-manifest.json.\nThe buyer ZIP contains START HERE.html and one recoup-plugin folder; local ZIP contains that folder contents.\nThe Claude ZIP and generated claude/ tree use the same customer content. Host submission/approval remains separate.
''')
    if chatgpt_app_id:
        with (out/'OPENAI-SUBMISSION.md').open('a') as instructions:
            instructions.write(f'\nWorkspace testing: upload `recoup-workspace-{version}.zip` to the ChatGPT workspace plugin.\nIt references the registered app `{chatgpt_app_id}` and requires access to that app.\nDo not use this workspace-specific ZIP for public directory submission.\n')


def release_provenance(files, version, commit):
    content = {name: hashlib.sha256(data).hexdigest() for name, data in files.items() if name.startswith('skills/')}
    digest = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'version': version, 'commit': commit, 'customer_content_sha256': digest}

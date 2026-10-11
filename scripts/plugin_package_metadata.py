"""Host-specific metadata and submission instructions for generated packages."""
import json

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
            if name == '.codex-plugin/plugin.json':
                host = 'ChatGPT' if customer else 'Codex'
                metadata.setdefault('interface', {})['shortDescription'] = f'A record label inside {host}'
                if customer:
                    icon = 'assets/recoup-customer-icon.png'
                    if icon not in files:
                        raise ValueError(f'Missing customer icon: {icon}')
                    metadata['interface']['logo'] = f'./{icon}'
                    metadata['interface']['composerIcon'] = f'./{icon}'
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

The full ZIP contains all staff and customer skills. Both packages come from this commit.
Checksums and complete skill inventories are in release-manifest.json.
''')
    if chatgpt_app_id:
        with (out/'OPENAI-SUBMISSION.md').open('a') as instructions:
            instructions.write(f'\nWorkspace testing: upload `recoup-workspace-{version}.zip` to the ChatGPT workspace plugin.\nIt references the registered app `{chatgpt_app_id}` and requires access to that app.\nDo not use this workspace-specific ZIP for public directory submission.\n')

#!/usr/bin/env python3
"""Fail before publication if customer content, provenance or host adapters drift."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

MCP = {'mcpServers': {'recoup': {'type': 'http', 'url': 'https://api.recoupable.dev/mcp'}}}
CURSOR_MCP = {'mcpServers': {'recoup': {'url': 'https://api.recoupable.dev/mcp'}}}
ADAPTERS = {
    'customer': ('.codex-plugin/plugin.json',),
    'workspace': ('.codex-plugin/plugin.json',),
    'local': ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.cursor-plugin/plugin.json'),
    'buyer': ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.cursor-plugin/plugin.json'),
    'claude': ('.claude-plugin/plugin.json',),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_files(files, audience, report, metadata):
    if audience == 'buyer':
        if 'START HERE.html' not in files or any(not n.startswith('recoup-plugin/') and n != 'START HERE.html' for n in files):
            raise ValueError('Buyer wrapper must contain START HERE.html and one recoup-plugin folder')
        files = {name.removeprefix('recoup-plugin/'): data for name, data in files.items() if name.startswith('recoup-plugin/')}
        if any(name.endswith('.zip') for name in files):
            raise ValueError('Buyer wrapper must not contain nested ZIPs')
    expected = report['customer_content']
    actual = {name: digest(data) for name, data in sorted(files.items()) if name.startswith('skills/')}
    skills = sorted(name.split('/')[1] for name in actual if name.count('/') == 2 and name.endswith('/SKILL.md'))
    if actual != expected['files'] or skills != expected['skills'] or metadata['skills'] != skills:
        raise ValueError(f'{audience}: customer skill content/inventory differs')
    if any(name.startswith('recoup-internal-') for name in skills):
        raise ValueError(f'{audience}: internal skill leaked')
    if metadata['customer_content_sha256'] != expected['sha256']:
        raise ValueError(f'{audience}: customer content digest differs')
    provenance = {'version': report['version'], 'commit': report['commit'], 'customer_content_sha256': expected['sha256']}
    if json.loads(files.get('RELEASE.json', b'{}')) != provenance:
        raise ValueError(f'{audience}: source/version provenance differs')
    adapters = ADAPTERS[audience]
    found = {name for name in files if name.endswith('/plugin.json') and name.startswith(('.codex-plugin/', '.claude-plugin/', '.cursor-plugin/'))}
    if found != set(adapters):
        raise ValueError(f'{audience}: missing or unexpected host adapter')
    for name in adapters:
        plugin = json.loads(files[name])
        expected_name = metadata.get('package_name', 'recoup-plugin') if audience == 'workspace' else 'recoup-plugin'
        if plugin.get('version') != report['version'] or plugin.get('name') != expected_name:
            raise ValueError(f'{audience}: host name/version differs')
        if 'hooks' in plugin:
            raise ValueError(f'{audience}: unexpected lifecycle hooks')
        if audience == 'workspace':
            expected_app = {'apps': {'recoup': {'id': metadata['chatgpt_app_id'], 'required': True}}}
            if plugin.get('apps') != './.app.json' or 'mcpServers' in plugin or '.mcp.json' in files or json.loads(files.get('.app.json', b'{}')) != expected_app:
                raise ValueError('workspace: registered app mapping differs')
        else:
            config = 'mcp.json' if name.startswith('.cursor-plugin/') else '.mcp.json'
            expected_mcp = CURSOR_MCP if config == 'mcp.json' else MCP
            if plugin.get('mcpServers') != './'+config or 'apps' in plugin or '.app.json' in files or json.loads(files.get(config, b'{}')) != expected_mcp:
                raise ValueError(f'{audience}: Recoup MCP mapping differs')


def validate(out):
    report = json.loads((out/'release-manifest.json').read_text())
    expected = report['customer_content']
    calculated = digest(json.dumps(expected['files'], sort_keys=True, separators=(',', ':')).encode())
    if calculated != expected['sha256'] or calculated != report['customer_content_sha256']:
        raise ValueError('Customer content manifest digest differs')
    required = {'customer', 'full', 'local', 'buyer', 'claude'}
    if not required.issubset(report['packages']):
        raise ValueError('Missing release artifact')
    for audience, metadata in report['packages'].items():
        path = out/metadata['file']
        if digest(path.read_bytes()) != metadata['sha256']:
            raise ValueError(f'{audience}: archive checksum differs')
        with zipfile.ZipFile(path) as archive:
            if len(archive.namelist()) != len(set(archive.namelist())):
                raise ValueError(f'{audience}: duplicate archive member')
            files = {name: archive.read(name) for name in archive.namelist()}
        if audience == 'full':
            for name, data in files.items():
                if name.endswith(('plugin.json', 'marketplace.json')):
                    def versions(value):
                        if isinstance(value, dict):
                            for key, item in value.items():
                                if key == 'version' and item != report['version']:
                                    raise ValueError('full: manifest version differs')
                                versions(item)
                        elif isinstance(value, list):
                            for item in value: versions(item)
                    versions(json.loads(data))
            continue
        if audience not in ADAPTERS:
            raise ValueError(f'Unknown adapter: {audience}')
        validate_files(files, audience, report, metadata)
        if audience == 'claude':
            tree = out/metadata['tree']
            tree_files = {p.relative_to(tree).as_posix(): p.read_bytes() for p in tree.rglob('*') if p.is_file()}
            if tree_files != files:
                raise ValueError('Claude tree differs from release archive')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    validate(args.out)
    print('Release parity passed: customer content, host adapters, archive checksums and Claude tree')

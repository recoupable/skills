#!/usr/bin/env python3
"""Build customer/full plugin ZIPs from tracked files, without modifying source manifests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
from plugin_package_metadata import prepare_metadata, write_handoff
from plugin_package_dependencies import validate_customer_dependencies

ROOT = Path(__file__).resolve().parents[1]
from plugin_package_files import package_files

def build(root, tracked, out, version, commit, chatgpt_app_id=None, workspace_name=None):
    if chatgpt_app_id and not re.fullmatch(r"asdk_app_[a-zA-Z0-9][a-zA-Z0-9_-]*", chatgpt_app_id):
        raise ValueError("ChatGPT app ID must be asdk_app_ followed by letters, digits, underscores or hyphens")
    if workspace_name and (not chatgpt_app_id or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', workspace_name)):
        raise ValueError('Workspace name requires an app ID and a lowercase hyphenated package name')
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Version must be numeric semantic version')
    tracked = list(tracked)
    out.mkdir(parents=True, exist_ok=True)
    from build_claude_package import customer_tree_files
    from plugin_buyer_guide import guide
    from validate_release_parity import validate
    customer_files, customer_skills = package_files(root, tracked, 'customer')
    content = {name: hashlib.sha256(data).hexdigest() for name, data in customer_files.items() if name.startswith('skills/')}
    content_digest = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    provenance = {'version': version, 'commit': commit, 'customer_content_sha256': content_digest}
    provenance_bytes = (json.dumps(provenance, indent=2)+'\n').encode()
    manifest = {**provenance, 'openai_status': 'upload_and_review_required',
                'claude_status': 'submission_and_review_required',
                'customer_content': {'skills': customer_skills, 'files': content, 'sha256': content_digest},
                'packages': {}}
    variants = {}
    for audience in ('customer', 'full') + (('workspace',) if chatgpt_app_id else ()):
        files, skills = package_files(root, tracked, 'full' if audience == 'full' else 'customer')
        prepare_metadata(files, audience, version, chatgpt_app_id, workspace_name)
        files['RELEASE.json'] = provenance_bytes
        variants[audience] = (files, skills)
    local = dict(customer_files)
    for name in ('.claude-plugin/plugin.json', '.cursor-plugin/plugin.json', 'mcp.json'):
        if name not in tracked or not (root/name).is_file():
            raise ValueError(f'Missing tracked host adapter: {name}')
        local[name] = (root/name).read_bytes()
    prepare_metadata(local, 'local', version, chatgpt_app_id, workspace_name)
    local['RELEASE.json'] = provenance_bytes
    variants['local'] = (local, customer_skills)
    buyer = {'START HERE.html': guide(version, commit), **{f'recoup-plugin/{name}': data for name, data in local.items()}}
    variants['buyer'] = (buyer, customer_skills)
    claude, skills = customer_tree_files(root, tracked, version, commit)
    claude['RELEASE.json'] = provenance_bytes
    variants['claude'] = (claude, skills)
    claude_dir = out/'claude'
    if claude_dir.exists() and any(claude_dir.iterdir()):
        raise ValueError('Claude output directory must be empty')
    for name, data in claude.items():
        path = claude_dir/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if (root/name).is_file() and (root/name).stat().st_mode & 0o111:
            path.chmod(0o755)
    for audience, (files, skills) in variants.items():
        filename = f'recoup-{audience}-{version}.zip'
        with zipfile.ZipFile(out/filename, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                source = name.removeprefix('recoup-plugin/')
                info.external_attr = (0o100755 if (root/source).is_file() and (root/source).stat().st_mode & 0o111 else 0o100644) << 16
                archive.writestr(info, data)
        manifest['packages'][audience] = {'file': filename, 'skills': skills,
            'customer_content_sha256': content_digest if audience != 'full' else None,
            'sha256': hashlib.sha256((out/filename).read_bytes()).hexdigest()}
    manifest['packages']['claude']['tree'] = 'claude'
    if chatgpt_app_id:
        manifest['packages']['workspace']['chatgpt_app_id'] = chatgpt_app_id
        manifest['packages']['workspace']['package_name'] = workspace_name or 'recoup-plugin'
    (out/'release-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    validate(out)
    write_handoff(out, version, commit, chatgpt_app_id)
    return manifest

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--chatgpt-app-id', default=os.environ.get('CHATGPT_APP_ID') or None)
    parser.add_argument('--workspace-name', default=os.environ.get('CHATGPT_WORKSPACE_PACKAGE_NAME') or None)
    args=parser.parse_args()
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report=build(ROOT,filter(None,tracked),args.out,args.version,commit,args.chatgpt_app_id,args.workspace_name)
    print(json.dumps({k:len(v['skills']) for k,v in report['packages'].items()}))

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

ROOT = Path(__file__).resolve().parents[1]
INTERNAL = re.compile(r'\brecoup-internal-[a-z0-9-]+')

def package_files(root, tracked, audience):
    result = {}
    for name in sorted(tracked):
        p = root / name
        parts = Path(name).parts
        if not p.is_file():
            continue
        if p.is_symlink() and not p.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'External symlink: {name}')
        if audience == 'customer':
            if not (name in {'.codex-plugin/plugin.json', '.mcp.json', 'LICENSE'} or
                    parts[0] == 'assets' or
                    (parts[0] == 'skills' and len(parts) > 2 and not parts[1].startswith('recoup-internal-'))):
                continue
        elif parts[0] in {'.github', '.git'}:
            continue
        data = p.read_bytes()
        if audience == 'customer' and parts[0] == 'skills':
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                text = ''
            if INTERNAL.search(text):
                raise ValueError(f'Customer file references excluded internal skill: {name}')
        result[name] = data
    for required in ('.codex-plugin/plugin.json', '.mcp.json'):
        if required not in result:
            raise ValueError(f'Missing {required}')
    skills = sorted(n.split('/')[1] for n in result if re.fullmatch(r'skills/[^/]+/SKILL.md', n))
    if not skills:
        raise ValueError('No skills packaged')
    return result, skills

def build(root, tracked, out, version, commit, chatgpt_app_id=None, workspace_name=None):
    if chatgpt_app_id and not re.fullmatch(r"asdk_app_[a-zA-Z0-9][a-zA-Z0-9_-]*", chatgpt_app_id):
        raise ValueError("ChatGPT app ID must be asdk_app_ followed by letters, digits, underscores or hyphens")
    if workspace_name and (not chatgpt_app_id or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', workspace_name)):
        raise ValueError('Workspace name requires an app ID and a lowercase hyphenated package name')
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Version must be numeric semantic version')
    tracked = list(tracked)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'version': version, 'commit': commit, 'openai_status': 'upload_and_review_required', 'packages': {}}
    audiences = ('customer', 'full', 'workspace') if chatgpt_app_id else ('customer', 'full')
    for audience in audiences:
        customer = audience != 'full'
        files, skills = package_files(root, tracked, 'customer' if customer else 'full')
        prepare_metadata(files, audience, version, chatgpt_app_id, workspace_name)
        filename = f'recoup-{audience}-{version}.zip'
        with zipfile.ZipFile(out/filename,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2020,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if (root/name).exists() and (root/name).stat().st_mode & 0o111 else 0o100644) << 16
                z.writestr(info,data)
        manifest['packages'][audience] = {'file':filename,'skills':skills,'sha256':hashlib.sha256((out/filename).read_bytes()).hexdigest()}
    if chatgpt_app_id:
        manifest['packages']['workspace']['chatgpt_app_id'] = chatgpt_app_id
        if workspace_name:
            manifest['packages']['workspace']['package_name'] = workspace_name
    (out/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
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

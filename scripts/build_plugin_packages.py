#!/usr/bin/env python3
"""Build customer/full plugin ZIPs from tracked files, without modifying source manifests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

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

def stamp_versions(value, version):
    if isinstance(value, dict):
        return {k: version if k == 'version' else stamp_versions(v, version) for k,v in value.items()}
    if isinstance(value, list):
        return [stamp_versions(v, version) for v in value]
    return value

def build(root, tracked, out, version, commit):
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Version must be numeric semantic version')
    tracked = list(tracked)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'version': version, 'commit': commit, 'openai_status': 'upload_and_review_required', 'packages': {}}
    for audience in ('customer', 'full'):
        files, skills = package_files(root, tracked, audience)
        for name in files:
            if name.endswith(('plugin.json','marketplace.json')) and name.startswith(('.codex-plugin/', '.claude-plugin/', '.cursor-plugin/', '.agents/plugins/')):
                files[name] = (json.dumps(stamp_versions(json.loads(files[name]),version),indent=2)+'\n').encode()
        filename = f'recoup-{audience}-{version}.zip'
        with zipfile.ZipFile(out/filename,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2020,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if (root/name).stat().st_mode & 0o111 else 0o100644) << 16
                z.writestr(info,data)
        manifest['packages'][audience] = {'file':filename,'skills':skills,'sha256':hashlib.sha256((out/filename).read_bytes()).hexdigest()}
    (out/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'OPENAI-SUBMISSION.md').write_text(f'''# Recoup {version}

Source commit: {commit}

Upload `recoup-customer-{version}.zip` to the existing Recoup draft in the OpenAI
publisher dashboard. Do not upload the full staff package to the public directory.
Resolve scans, complete MCP/reviewer setup, submit for review, then publish after approval.
This GitHub release is not evidence of OpenAI approval or publication.

The full ZIP contains all staff and customer skills. Both packages come from this commit.
Checksums and complete skill inventories are in release-manifest.json.
''')
    return manifest

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report=build(ROOT,filter(None,tracked),args.out,args.version,commit)
    print(json.dumps({k:len(v['skills']) for k,v in report['packages'].items()}))

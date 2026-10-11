"""Export the customer skill boundary as a Claude directory source tree."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from build_plugin_packages import package_files
from plugin_package_metadata import stamp_versions

ROOT = Path(__file__).resolve().parents[1]


def build(root, tracked, out, version, commit):
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Version must be numeric semantic version')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be empty')
    files, skills = package_files(root, tracked, 'customer')
    files.pop('.codex-plugin/plugin.json')
    metadata = stamp_versions(json.loads((root/'.claude-plugin/plugin.json').read_text()), version)
    files['.claude-plugin/plugin.json'] = (json.dumps(metadata, indent=2)+'\n').encode()
    files['README.md'] = ('''# Recoup

A record label inside Claude for artists, managers, and labels. Research artists,
organize catalogs, plan releases, and create release assets. Start with a song,
an artist, or an entire catalog, and put your agents to work.

## Connect and use

Install the plugin, connect the Recoup MCP server, and sign in to your Recoup
account through OAuth. Ask Claude to open Recoup workflows, research an artist,
or find songs in a catalog you can access. Available customer skills are listed below.
Some tools require Recoup credits or additional account entitlements. Review
proposed publishing, sending, and other external actions before authorizing them.

Documentation: https://docs.recoupable.dev
Support: agent@recoupable.dev
Privacy: https://recoupable.dev/privacy

## Included skills

''' + ''.join(f'- {name}\n' for name in skills) +
        f'\n## Release provenance\n\nSource commit: {commit}\nVersion: {version}\n').encode()
    if 'LICENSE' not in files:
        raise ValueError('Missing LICENSE')
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = out/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if (root/name).is_file() and (root/name).stat().st_mode & 0o111:
            path.chmod(0o755)
    return skills


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(json.dumps(build(ROOT, filter(None, tracked), args.out, args.version, commit)))

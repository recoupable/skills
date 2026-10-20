"""Export the customer skill boundary as a Claude directory source tree."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from plugin_package_files import package_files
from plugin_package_metadata import stamp_versions, release_provenance

ROOT = Path(__file__).resolve().parents[1]


def customer_tree_files(root, tracked, version, commit):
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Version must be numeric semantic version')
    files, skills = package_files(root, tracked, 'customer')
    files.pop('.codex-plugin/plugin.json')
    metadata = stamp_versions(json.loads((root/'.claude-plugin/plugin.json').read_text()), version)
    if 'assets/recoup-customer-icon.png' not in files:
        raise ValueError('Missing customer icon')
    # Keep listing artwork separate from skill-local assets/template directories.
    for name in list(files):
        if name.startswith('assets/'):
            files['branding/' + name.removeprefix('assets/')] = files.pop(name)
    metadata['icon'] = './branding/recoup-customer-icon.png'
    metadata['privacyPolicyUrl'] = 'https://recoupable.dev/privacy'
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

## Execution and authentication

The declared MCP server uses remote HTTPS and host-managed OAuth. This package
does not register installation commands, lifecycle hooks, or a local MCP server.
That does not mean every workflow is remote-only: skills include readable Python,
JavaScript, and shell helpers that Claude may run for a user-requested task in a
host that supports execution. Other workflows can generate site or workspace code.
Inspect the skill and its scripts before granting execution permission.

Prefer connected MCP tools. Optional REST examples and helpers use separately
configured Recoup credentials, not tokens extracted from the host's OAuth session.
Catalog research and email helpers can call the Recoup API directly. Do not read
unrelated credentials or send Recoup credentials to another service. If a required
tool, credential, or execution capability is unavailable, report that limitation.
The bundled helper inventory below is generated from this exact release.

## Data handling and optional services

The declared connector is Recoup at api.recoupable.dev. Authorized workflows can
read and save artist, contact, catalog, release, and account information. Saved
Recoup content can remain longer than 30 days, until deletion or an applicable
retention requirement ends; disconnecting Claude does not delete the account.
See the privacy policy for retention, deletion, processors, and public assets.

Some skills also describe optional tools outside the declared Recoup connector.
ElevenLabs Scribe receives selected audio for transcription. Creative and site
workflows can use separately connected Higgsfield tools or a provider selected
by the user, such as fal.ai, receiving the prompts and reference assets needed
for that step. A user-selected hosting service can receive site files when
publishing is requested. These integrations require their own access and user
authorization; installing this plugin does not grant it. Review the destination
and inputs before sending data. External services apply their own privacy and
retention policies. The plugin is not specifically intended for users under 18.

## Included skills

''' + ''.join(f'- {name}\n' for name in skills) +
        '\n## Bundled helpers\n\n' + ''.join(
            f'- {name}\n' for name in sorted(files)
            if name.startswith('skills/') and Path(name).suffix in {'.py', '.mjs', '.js', '.sh'}
        ) +
        f'\n## Release provenance\n\nSource commit: {commit}\nVersion: {version}\n').encode()
    if 'LICENSE' not in files:
        raise ValueError('Missing LICENSE')
    files['RELEASE.json'] = (json.dumps(release_provenance(files, version, commit), indent=2)+'\n').encode()
    return files, skills


def build(root, tracked, out, version, commit):
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be empty')
    files, skills = customer_tree_files(root, tracked, version, commit)
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

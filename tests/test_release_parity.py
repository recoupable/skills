"""Release artifacts must be interchangeable customer content, not parallel copies."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_plugin_packages import build
from validate_release_parity import validate


class ReleaseParityTest(unittest.TestCase):
    def fixture(self, root):
        files = {
            '.codex-plugin/plugin.json': {'name': 'recoup-plugin', 'version': '1.0.0', 'skills': './skills/', 'mcpServers': './.mcp.json'},
            '.claude-plugin/plugin.json': {'name': 'recoup-plugin', 'version': '1.0.0', 'mcpServers': './.mcp.json'},
            '.cursor-plugin/plugin.json': {'name': 'recoup-plugin', 'version': '1.0.0', 'skills': './skills/', 'mcpServers': './mcp.json'},
            '.mcp.json': {'mcpServers': {'recoup': {'type': 'http', 'url': 'https://api.recoupable.dev/mcp'}}},
            'mcp.json': {'mcpServers': {'recoup': {'url': 'https://api.recoupable.dev/mcp'}}},
            'LICENSE': 'license', 'assets/recoup-customer-icon.png': 'icon',
            'skills/recoup-public/SKILL.md': 'Public',
            'skills/recoup-public/references/brief.md': 'Brief',
            'skills/recoup-internal-staff/SKILL.md': 'Staff',
        }
        for name, value in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value) if isinstance(value, dict) else value)
        return list(files)

    def test_all_adapters_share_content_and_buyer_has_one_install_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = build(root, self.fixture(root), root / 'out', '2026.1020.1', 'source', 'asdk_app_example', 'recoup-skills')
            self.assertEqual(set(report['packages']), {'customer', 'full', 'workspace', 'local', 'buyer', 'claude'})
            self.assertEqual(report['customer_content']['skills'], ['recoup-public'])
            self.assertEqual(len(report['customer_content']['files']), 2)
            validate(root / 'out')
            with zipfile.ZipFile(root / 'out' / report['packages']['buyer']['file']) as archive:
                self.assertIn('START HERE.html', archive.namelist())
                self.assertIn('recoup-plugin/.claude-plugin/plugin.json', archive.namelist())
                self.assertIn('recoup-plugin/.codex-plugin/plugin.json', archive.namelist())
                self.assertIn('recoup-plugin/.cursor-plugin/plugin.json', archive.namelist())
                self.assertFalse(any(name.endswith('.zip') for name in archive.namelist()))
            again = build(root, self.fixture(root), root / 'again', '2026.1020.1', 'source', 'asdk_app_example', 'recoup-skills')
            self.assertEqual(report, again)

    def test_modified_artifacts_fail_even_if_archive_checksum_is_updated(self):
        for mutation in ('changed_byte', 'omitted_skill', 'internal_skill', 'manifest_version', 'mcp_mapping', 'missing_adapter', 'claude_tree'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                report = build(root, self.fixture(root), root / 'out', '2026.1020.1', 'source', 'asdk_app_example', 'recoup-skills')
                if mutation == 'claude_tree':
                    (root / 'out/claude/skills/recoup-public/SKILL.md').write_text('Changed')
                else:
                    path = root / 'out' / report['packages']['local']['file']
                    with zipfile.ZipFile(path) as archive:
                        files = {name: archive.read(name) for name in archive.namelist()}
                    if mutation == 'changed_byte': files['skills/recoup-public/SKILL.md'] = b'Changed'
                    if mutation == 'omitted_skill': del files['skills/recoup-public/SKILL.md']
                    if mutation == 'internal_skill': files['skills/recoup-internal-staff/SKILL.md'] = b'Staff'
                    if mutation == 'manifest_version':
                        metadata = json.loads(files['.claude-plugin/plugin.json']); metadata['version'] = '0.0.0'
                        files['.claude-plugin/plugin.json'] = json.dumps(metadata).encode()
                    if mutation == 'mcp_mapping': files['mcp.json'] = b'{"mcpServers":{}}'
                    if mutation == 'missing_adapter': del files['.cursor-plugin/plugin.json']
                    with zipfile.ZipFile(path, 'w') as archive:
                        for name, data in files.items(): archive.writestr(name, data)
                    import hashlib
                    report['packages']['local']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                    (root / 'out/release-manifest.json').write_text(json.dumps(report))
                with self.assertRaises(ValueError): validate(root / 'out')


if __name__ == '__main__': unittest.main()

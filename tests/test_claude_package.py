import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_claude_package import build


class ClaudePackageTest(unittest.TestCase):
    def test_customer_boundary_and_claude_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                '.claude-plugin/plugin.json': json.dumps({'name': 'recoup-plugin', 'version': '1.0.0', 'mcpServers': './.mcp.json'}),
                '.codex-plugin/plugin.json': '{}', '.mcp.json': '{"mcpServers":{}}',
                'assets/recoup-customer-icon.png': 'icon-fixture',
                'LICENSE': 'license', 'skills/recoup-research/SKILL.md': 'Research',
                'skills/recoup-research/scripts/run.sh': '#!/bin/sh\ntrue\n',
                'skills/recoup-internal-staff/SKILL.md': 'Staff',
            }
            for name, data in files.items():
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(data)
            (root/'skills/recoup-research/scripts/run.sh').chmod(0o755)
            out = root/'out'
            self.assertEqual(build(root, files, out, '2026.1011.1', 'source'), ['recoup-research'])
            self.assertFalse((out/'skills/recoup-internal-staff').exists())
            self.assertFalse((out/'.codex-plugin').exists())
            self.assertEqual(json.loads((out/'.claude-plugin/plugin.json').read_text())['version'], '2026.1011.1')
            manifest = json.loads((out/'.claude-plugin/plugin.json').read_text())
            self.assertEqual(manifest['icon'], './branding/recoup-customer-icon.png')
            self.assertTrue((out/'branding/recoup-customer-icon.png').is_file())
            self.assertFalse((out/'assets').exists())
            self.assertIn('skills/recoup-research/scripts/run.sh', (out/'README.md').read_text())
            self.assertIn('does not mean every workflow is remote-only', (out/'README.md').read_text())
            self.assertEqual(manifest['privacyPolicyUrl'], 'https://recoupable.dev/privacy')
            self.assertIn('Source commit: source', (out/'README.md').read_text())
            self.assertTrue((out/'skills/recoup-research/scripts/run.sh').stat().st_mode & 0o111)
            with self.assertRaisesRegex(ValueError, 'empty'):
                build(root, files, out, '2026.1011.2', 'next')
            (root/'skills/recoup-research/SKILL.md').write_text('Use recoup-internal-staff')
            with self.assertRaisesRegex(ValueError, 'excluded internal'):
                build(root, files, root/'other', '2026.1011.2', 'next')

if __name__ == '__main__':
    unittest.main()

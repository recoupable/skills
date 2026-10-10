import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec=importlib.util.spec_from_file_location('packages',Path(__file__).resolve().parents[1]/'scripts/build_plugin_packages.py')
packages=importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)

class PackagesTest(unittest.TestCase):
    def fixture(self, root):
        files={'.codex-plugin/plugin.json':json.dumps({'version':'1.0.0','skills':'./skills/'}),
               '.mcp.json':'{"mcpServers":{}}',
               'assets/recoup-customer-icon.png':'customer-icon-fixture',
               'skills/recoup-public/SKILL.md':'Public instructions',
               'skills/recoup-internal-staff/SKILL.md':'Staff instructions',
               'skills/recoup-public/references/data.txt':'Bundled reference'}
        for n,text in files.items():
            p=root/n; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
        return list(files)

    def test_separate_packages_and_stamped_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            report=packages.build(root,iter(files),root/'out','2026.1008.1','test-commit')
            self.assertEqual(len(report['packages']['customer']['skills']),1)
            self.assertEqual(len(report['packages']['full']['skills']),2)
            with zipfile.ZipFile(root/'out'/report['packages']['customer']['file']) as z:
                self.assertIn('skills/recoup-public/references/data.txt',z.namelist())
                self.assertEqual(json.loads(z.read('.codex-plugin/plugin.json'))['interface']['logo'], './assets/recoup-customer-icon.png')
                self.assertEqual(z.read('assets/recoup-customer-icon.png'), b'customer-icon-fixture')
                self.assertFalse(any('recoup-internal-' in n for n in z.namelist()))
                self.assertEqual(json.loads(z.read('.codex-plugin/plugin.json'))['version'],'2026.1008.1')
                self.assertEqual(json.loads(z.read('.codex-plugin/plugin.json'))['interface']['shortDescription'], 'A record label inside ChatGPT')
            with zipfile.ZipFile(root/'out'/report['packages']['full']['file']) as z:
                self.assertEqual(json.loads(z.read('.codex-plugin/plugin.json'))['interface']['shortDescription'], 'A record label inside Codex')
            self.assertEqual(json.loads((root/'.codex-plugin/plugin.json').read_text())['version'],'1.0.0')
            again=packages.build(root,files,root/'again','2026.1008.1','test-commit')
            self.assertEqual(report,again)

    def test_new_customer_skill_is_automatically_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            n='skills/recoup-new/SKILL.md'; (root/n).parent.mkdir(); (root/n).write_text('New skill')
            _,skills=packages.package_files(root,files+[n],'customer')
            self.assertIn('recoup-new',skills)

    def test_internal_dependency_blocks_customer_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            (root/'skills/recoup-public/references/data.txt').write_text('Run recoup-internal-staff')
            with self.assertRaisesRegex(ValueError,'excluded internal'):
                packages.package_files(root,files,'customer')

if __name__=='__main__': unittest.main()

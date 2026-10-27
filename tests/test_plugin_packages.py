import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))

spec=importlib.util.spec_from_file_location('packages',Path(__file__).resolve().parents[1]/'scripts/build_plugin_packages.py')
packages=importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)

class PackagesTest(unittest.TestCase):
    def test_customer_recovery_examples_execute_from_foreign_working_directory(self):
        source_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracked = subprocess.check_output(
                ["git", "ls-files", "-z"], cwd=source_root, text=True,
            ).split("\0")
            report = packages.build(
                source_root, filter(None, tracked), root / "packages", "0.0.0", "local-fixture",
            )
            install = root / "isolated-install"
            with zipfile.ZipFile(root / "packages" / report["packages"]["customer"]["file"]) as archive:
                archive.extractall(install)
            foreign = root / "unrelated-project"
            foreign.mkdir()
            command = [
                sys.executable, str(source_root / "tests/test_billing_recovery_examples.py"),
                "--installed-root", str(install),
            ]
            def run_installed():
                return subprocess.run(
                    command, cwd=foreign, capture_output=True, text=True, timeout=60,
                )
            result = run_installed()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Ran 35 tests", result.stderr)
            self.assertIn("OK", result.stderr)
            for name in (
                "skills/recoup-content-make-video/references/research-context.md",
                "skills/recoup-catalog-estimate-value/scripts/estimate.py",
            ):
                with self.subTest(missing_packaged_file=name):
                    packaged = install / name
                    original = packaged.read_bytes()
                    try:
                        packaged.unlink()
                        failed = run_installed()
                        self.assertNotEqual(failed.returncode, 0, "Must not fall back to source files")
                        self.assertIn("FileNotFoundError", failed.stderr)
                    finally:
                        packaged.write_bytes(original)

    def fixture(self, root):
        files={'.codex-plugin/plugin.json':json.dumps({'version':'1.0.0','skills':'./skills/','mcpServers':'./.mcp.json'}),
               '.mcp.json':'{"mcpServers":{"recoup":{"type":"http","url":"https://api.recoupable.dev/mcp"}}}',
               'mcp.json':'{"mcpServers":{"recoup":{"url":"https://api.recoupable.dev/mcp"}}}',
               '.claude-plugin/plugin.json':json.dumps({'name':'recoup-plugin','version':'1.0.0','mcpServers':'./.mcp.json'}),
               '.cursor-plugin/plugin.json':json.dumps({'name':'recoup-plugin','version':'1.0.0','mcpServers':'./mcp.json','skills':'./skills/'}),
               'LICENSE':'license',
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
                review = json.loads(z.read('.codex-plugin/plugin.json'))['extensions']['com.openai']['review']
                self.assertIs(review['commerce'], False)
                self.assertIn('already available', review['commerce_description'])
                self.assertNotIn('test_credentials', review)
                self.assertNotIn('reviewer_instructions', review)
            with zipfile.ZipFile(root/'out'/report['packages']['full']['file']) as z:
                self.assertEqual(json.loads(z.read('.codex-plugin/plugin.json'))['interface']['shortDescription'], 'A record label inside Codex')
            self.assertEqual(json.loads((root/'.codex-plugin/plugin.json').read_text())['version'],'1.0.0')
            again=packages.build(root,files,root/'again','2026.1008.1','test-commit')
            self.assertEqual(report,again)

    def test_workspace_uses_registered_app_without_direct_mcp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            path=root/'.codex-plugin/plugin.json'
            metadata=json.loads(path.read_text()); metadata['mcpServers']='./.mcp.json'
            path.write_text(json.dumps(metadata))
            report=packages.build(root, files, root/'out', '2026.1011.1', 'test', 'asdk_app_example-1_x', 'recoup-skills')
            with zipfile.ZipFile(root/'out'/report['packages']['workspace']['file']) as z:
                manifest=json.loads(z.read('.codex-plugin/plugin.json'))
                self.assertEqual(manifest['name'], 'recoup-skills')
                self.assertNotIn('mcpServers', manifest)
                self.assertNotIn('.mcp.json', z.namelist())
                self.assertEqual(manifest['apps'], './.app.json')
                self.assertEqual(json.loads(z.read('.app.json')), {'apps': {'recoup': {'id':'asdk_app_example-1_x', 'required':True}}})
                self.assertEqual(manifest['interface']['logo'], './assets/recoup-customer-icon.png')
                self.assertFalse(any('recoup-internal-' in n for n in z.namelist()))
            with zipfile.ZipFile(root/'out'/report['packages']['customer']['file']) as z:
                self.assertIn('.mcp.json', z.namelist())
                self.assertNotIn('.app.json', z.namelist())
            self.assertEqual(report['packages']['workspace']['skills'], report['packages']['customer']['skills'])
            again=packages.build(root, files, root/'again', '2026.1011.1', 'test', 'asdk_app_example-1_x', 'recoup-skills')
            self.assertEqual(report, again)
            with self.assertRaisesRegex(ValueError, 'ChatGPT app ID'):
                packages.build(root, files, root/'bad', '2026.1011.1', 'test', 'plugin_asdk_app_example')

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

    def test_customer_release_rejects_transaction_and_credential_collection_paths(self):
        for instructions in (
            'POST /api/subscriptions/sessions to open checkout',
            'POST /api/credits/sessions to buy credits',
            'Go to https://checkout.stripe.com/c/pay_fixture',
            'POST /api/agents/verify with the emailed code',
            'Use the existing customer checkout path; after checkout, retry activation.',
        ):
            with self.subTest(instructions=instructions), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); files=self.fixture(root)
                (root/'skills/recoup-public/SKILL.md').write_text(instructions)
                with self.assertRaisesRegex(ValueError, 'Customer commerce/auth boundary'):
                    packages.package_files(root,files,'customer')

    def test_customer_release_keeps_existing_entitlement_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            (root/'skills/recoup-public/SKILL.md').write_text(
                'Use connected OAuth and existing account entitlements. On 402 retain the job and stop. Never purchase credits.'
            )
            _, skills=packages.package_files(root,files,'customer')
            self.assertEqual(skills, ['recoup-public'])

    def test_missing_recoup_web_dependency_blocks_customer_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            skill=root/'skills/recoup-public/SKILL.md'
            skill.write_text('Use https://github.com/recoupable/skills/tree/main/skills/hyperframes')
            # A local but untracked dependency is still absent from the customer ZIP.
            dependency=root/'skills/hyperframes/SKILL.md'
            dependency.parent.mkdir(); dependency.write_text('Composition')
            with self.assertRaisesRegex(ValueError,'missing packaged Recoup path'):
                packages.build(root,files,root/'out','2026.1020.1','test')
            report=packages.build(root,files+['skills/hyperframes/SKILL.md'],root/'good','2026.1020.1','test')
            with zipfile.ZipFile(root/'good'/report['packages']['customer']['file']) as z:
                self.assertIn('skills/hyperframes/SKILL.md',z.namelist())

    def test_blob_reference_requires_the_packaged_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            skill=root/'skills/recoup-public/SKILL.md'
            skill.write_text('https://github.com/recoupable/skills/blob/main/skills/recoup-public/references/data.txt#example')
            packages.package_files(root,files,'customer')
            skill.write_text('https://github.com/recoupable/skills/blob/main/skills/recoup-public/references/missing.txt')
            with self.assertRaisesRegex(ValueError,'missing packaged Recoup path'):
                packages.package_files(root,files,'customer')

    def test_bundled_reference_must_ship_with_the_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            (root/'skills/recoup-public/SKILL.md').write_text('Read `references/composition.md`')
            with self.assertRaisesRegex(ValueError,'missing bundled file'):
                packages.package_files(root,files,'customer')
            name='skills/recoup-public/references/composition.md'
            (root/name).write_text('Local assembly; disclose unperformed reviews.')
            packages.package_files(root,files+[name],'customer')

    def test_supporting_prose_examples_are_not_declared_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            name='skills/recoup-public/references/authoring.md'
            (root/name).write_text('Example project layout:\n```text\nscripts/example.py\n```')
            packages.package_files(root,files+[name],'customer')

    def test_required_normalizer_in_supporting_guide_must_ship(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            guide='skills/recoup-public/references/normalization.md'
            script='skills/recoup-public/scripts/normalize-royalty-statement.py'
            (root/'skills/recoup-public/SKILL.md').write_text('Read `references/normalization.md`')
            (root/guide).write_text('Use `scripts/normalize-royalty-statement.py` for first-pass CSV normalization.')
            (root/script).parent.mkdir(); (root/script).write_text('print("fixture")')
            with self.assertRaisesRegex(ValueError,'normalization.md: scripts/normalize-royalty-statement.py'):
                packages.build(root,files+[guide],root/'missing','2026.1020.1','test')
            report=packages.build(root,files+[guide,script],root/'complete','2026.1020.1','test')
            with zipfile.ZipFile(root/'complete'/report['packages']['customer']['file']) as z:
                self.assertIn(script,z.namelist())

    def test_extensionless_and_directory_dependencies_must_ship(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            skill=root/'skills/recoup-public/SKILL.md'
            for relative in ['scripts/check', 'references/checks/', 'templates/']:
                skill.write_text(f'Read `{relative}`')
                with self.assertRaisesRegex(ValueError,'missing bundled file'):
                    packages.package_files(root,files,'customer')
                name='skills/recoup-public/'+relative+('guide.md' if relative.endswith('/') else '')
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                (root/name).write_text('Bundled fixture')
                packages.package_files(root,files+[name],'customer')

    def test_plain_recoup_url_ignores_sentence_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            (root/'skills/recoup-public/SKILL.md').write_text(
                'See https://github.com/recoupable/skills/tree/main/skills/recoup-public. '
                'Read https://github.com/recoupable/skills/blob/main/skills/recoup-public/references/data.txt, next.')
            packages.package_files(root,files,'customer')

    def test_markdown_support_links_are_checked_in_every_guide(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); files=self.fixture(root)
            guide='skills/recoup-public/references/next.md'
            (root/guide).write_text('Read [the helper](./scripts/build#usage).')
            (root/'skills/recoup-public/SKILL.md').write_text('Read [the guide](references/next.md).')
            with self.assertRaisesRegex(ValueError,'references/next.md'):
                packages.package_files(root,files,'customer')
            with self.assertRaisesRegex(ValueError,'scripts/build#usage'):
                packages.package_files(root,files+[guide],'customer')
            script='skills/recoup-public/scripts/build'
            (root/script).parent.mkdir(); (root/script).write_text('fixture')
            packages.package_files(root,files+[guide,script],'customer')

if __name__=='__main__': unittest.main()

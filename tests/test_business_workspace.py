"""Check the documented Mono/Business paths with synthetic workspace files only."""
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BusinessWorkspaceTests(unittest.TestCase):
    def check_paths(self, text, root):
        rows = {}
        for line in text.splitlines():
            cells = [value.strip().strip('`') for value in line.strip().strip('|').split('|')]
            if len(cells) == 3 and cells[0] in ('Mono root', 'Business root'):
                rows[cells[0]] = cells[1:]
        self.assertEqual(set(rows), {'Mono root', 'Business root'})
        expected = (root / 'skills').resolve()
        for label, start in [('Mono root', root), ('Business root', root / 'business')]:
            repository, authoring = rows[label]
            self.assertEqual((start / repository).resolve(), expected)
            skill = start / authoring.replace('<skill-name>', 'fixture-skill')
            self.assertEqual(skill.resolve(), expected / 'skills/fixture-skill/SKILL.md')
            self.assertEqual(skill.read_text(), 'synthetic skill definition\n')

    def fixture(self, root):
        # Include a plausible but wrong nested checkout. Mere file existence
        # must not make Business/plugin the owner of the shared Skills source.
        for repository in [root / 'skills', root / 'business/plugin']:
            skill = repository / 'skills/fixture-skill/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text('synthetic skill definition\n')

    def test_both_documented_starting_directories_reach_one_skills_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            self.check_paths((ROOT / 'README.md').read_text(), root)

    def test_nested_checkout_drift_is_rejected_even_if_that_directory_exists(self):
        source = (ROOT / 'README.md').read_text()
        changed = source.replace('`../skills/`', '`plugin/`').replace(
            '`../skills/skills/<skill-name>/SKILL.md`', '`plugin/skills/<skill-name>/SKILL.md`',
        )
        self.assertTrue(changed != source, 'README lacks the Business paths used by the drift probe')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            with self.assertRaises(AssertionError):
                self.check_paths(changed, root)

    def test_generic_commit_step_resolves_the_workspace_owner(self):
        skill = (ROOT / 'skills/recoup-internal-consulting-nightly-ingestion/SKILL.md').read_text()
        commit = skill.split('4. **Commit', 1)[1].split('5. **', 1)[0]
        self.assertNotIn('`plugin/`', commit)
        self.assertIn('selected workspace', commit)
        self.assertIn('Skills repository', commit)
        self.assertIn('separate', commit)


if __name__ == '__main__':
    unittest.main()

"""User-named skills must participate in the same routing audit as branded ones."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoutingTests(unittest.TestCase):
    def test_both_readers_include_custom_names_and_ignore_prose(self):
        audit = load('check_resolvable')
        evaluation = load('run_resolver_eval')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resolver = root / 'RESOLVER.md'
            resolver.write_text(
                '| Intent | Skill |\n|---|---|\n'
                '| Describe motion | `ui-design-vocabulary` |\n'
                '| Research | `recoup-research-the-web` |\n'
                '| Versioned | `recoup-internal-video-grok-1.5-demo` |\n'
                '| Missing | `missing-design-skill` |\n'
                'Prose mentions `unrouted-design-skill`.\n'
            )
            expected = {'ui-design-vocabulary', 'recoup-research-the-web',
                        'recoup-internal-video-grok-1.5-demo', 'missing-design-skill'}
            self.assertEqual(audit.routed_skills(resolver), expected)
            with patch.object(evaluation, 'PLUGIN', root):
                self.assertEqual(evaluation.routed_skills(), expected)
            # Unknown names remain visible so the audit can flag broken routes.
            self.assertIn('missing-design-skill', audit.routed_skills(resolver))


if __name__ == '__main__':
    unittest.main()

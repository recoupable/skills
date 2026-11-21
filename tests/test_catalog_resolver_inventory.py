import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class ResolverGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "plugin"
        scripts = self.root / "scripts"
        scripts.mkdir(parents=True)
        source = Path(__file__).resolve().parents[1] / "scripts"
        for name in ("check_resolvable.py", "run_resolver_eval.py", "resolver_catalog.py"):
            shutil.copyfile(source / name, scripts / name)
        self.skills = ["recoup-roster-add-artist", "ui-design-vocabulary", "video-grok-1.5"]
        for name in self.skills:
            folder = self.root / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("---\nname: " + name + "\n---\n")
        (self.root / "resolver-eval.jsonl").write_text("".join(
            json.dumps({"intent": "Use " + name, "expected": name}) + "\n"
            for name in self.skills
        ))
        self.write_routes(self.skills)

    def write_routes(self, names):
        (self.root / "RESOLVER.md").write_text(
            "Prose is not a route: `nonexistent-prose-skill`.\n"
            + "".join("  | Request | `" + name + "` |\n" for name in names)
        )

    def run_gate(self, script, module=False):
        return subprocess.run(
            [sys.executable, "-m", "scripts." + Path(script).stem] if module else
            [sys.executable, str(self.root / "scripts" / script)],
            cwd=self.root if module else self.directory.name,
            env={**os.environ, "RECOUP_RESOLVER_EVAL_LLM": "0"},
            capture_output=True, text=True,
        )

    def assert_gates(self, exit_code, diagnostics=None, module=False):
        for script in ("check_resolvable.py", "run_resolver_eval.py"):
            with self.subTest(script=script):
                result = self.run_gate(script, module=module)
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                self.assertNotIn("Traceback (most recent call last)", result.stderr)
                if diagnostics:
                    self.assertIn(diagnostics[script], result.stdout)

    def test_real_table_routes_accept_named_and_dotted_skills_from_foreign_cwd(self):
        self.assert_gates(0)

    def test_package_module_entrypoints_keep_working(self):
        self.assert_gates(0, module=True)

    def test_prose_mention_cannot_hide_an_unrouted_skill(self):
        self.write_routes(self.skills[:-1])
        with (self.root / "RESOLVER.md").open("a") as resolver:
            resolver.write("See `" + self.skills[-1] + "` for details.\n")
        self.assert_gates(1, {
            "check_resolvable.py": "UNREACHABLE",
            "run_resolver_eval.py": "exists but is not routed",
        })

    def test_missing_skill_fails_both_existing_route_and_fixture(self):
        (self.root / "skills" / self.skills[-1] / "SKILL.md").unlink()
        self.assert_gates(1, {
            "check_resolvable.py": "BROKEN ROUTE",
            "run_resolver_eval.py": "is not a skill, none or clarify",
        })


if __name__ == "__main__":
    unittest.main()

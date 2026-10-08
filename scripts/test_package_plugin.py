"""Exercise artifact isolation and reproducibility using a temporary Git repo."""
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

import package_plugin


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        previous = package_plugin.ROOT
        package_plugin.ROOT = self.root
        self.addCleanup(setattr, package_plugin, "ROOT", previous)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Package Test")
        self.git("config", "commit.gpgsign", "false")
        for name in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
                     ".cursor-plugin/plugin.json", ".mcp.json", "mcp.json",
                     "gemini-extension.json", "README.md", "LICENSE",
                     "skills/example/SKILL.md", "skills/example/references/detail.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"committed content: {name}\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root)

    def test_committed_bytes_only_and_reproducible(self):
        (self.root / "skills/example/SKILL.md").write_text("uncommitted change")
        (self.root / "skills/example/.env").write_text("untracked secret")
        one = package_plugin.build(self.root / "one.zip", "HEAD")
        two = package_plugin.build(self.root / "two.zip", "HEAD")
        self.assertEqual(one["sha256"], two["sha256"])
        self.assertEqual(one["skills"], 1)
        with zipfile.ZipFile(self.root / "one.zip") as bundle:
            self.assertNotIn("skills/example/.env", bundle.namelist())
            self.assertEqual(bundle.read("skills/example/SKILL.md"),
                             b"committed content: skills/example/SKILL.md\n")
            self.assertIn("skills/example/references/detail.md", bundle.namelist())
        with self.assertRaises(FileExistsError):
            package_plugin.build(self.root / "one.zip", "HEAD")

    def test_rejects_component_symlinks(self):
        (self.root / "skills/example/leak").symlink_to("/etc/passwd")
        self.git("add", "skills/example/leak")
        self.git("commit", "-qm", "unsafe link")
        with self.assertRaisesRegex(ValueError, "Unsafe package member"):
            package_plugin.build(self.root / "unsafe.zip", "HEAD")


if __name__ == "__main__":
    unittest.main()

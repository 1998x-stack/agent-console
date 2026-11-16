"""P0A-T01: repository contract is intentionally tested before implementation."""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FoundationLayoutTests(unittest.TestCase):
    def test_required_files_exist(self):
        paths = [
            "Makefile", ".gitignore", "pyproject.toml", "package.json",
            "pnpm-workspace.yaml", "pnpm-lock.yaml",
            "apps/web/package.json", "services/api/pyproject.toml",
            "services/pi-worker/package.json", ".github/workflows/foundation-ci.yml",
            "scripts/not_implemented.py",
        ]
        for rel in paths:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file(), f"missing: {rel}")

    def test_pnpm_monorepo_configuration(self):
        package = json.loads((ROOT / "package.json").read_text("utf-8"))
        self.assertTrue(package["private"])
        self.assertRegex(package["packageManager"], r"^pnpm@\d+\.\d+\.\d+$")
        self.assertIn("check", package["scripts"])
        workspace = (ROOT / "pnpm-workspace.yaml").read_text("utf-8")
        self.assertIn("apps/*", workspace)
        self.assertIn("services/pi-worker", workspace)

    def test_real_make_targets_and_no_false_green(self):
        makefile = (ROOT / "Makefile").read_text("utf-8")
        for target in ("check", "docs-check", "test-unit", "test-contract",
                       "test-integration", "test-e2e", "test-security",
                       "compose-up", "compose-down"):
            with self.subTest(target=target):
                self.assertRegex(makefile, rf"(?m)^{re.escape(target)}:")
        gate = (ROOT / "scripts/not_implemented.py").read_text("utf-8")
        self.assertIn("NOT RUN", gate)
        self.assertIn("SystemExit(2)", gate)

    def test_monorepo_service_boundaries(self):
        for rel in ("apps/web/package.json", "services/pi-worker/package.json"):
            package = json.loads((ROOT / rel).read_text("utf-8"))
            self.assertTrue(package["private"])
            self.assertIn("name", package)
        api = (ROOT / "services/api/pyproject.toml").read_text("utf-8")
        self.assertIn("[project]", api)

    def test_ci_executes_real_tests(self):
        workflow = (ROOT / ".github/workflows/foundation-ci.yml").read_text("utf-8")
        self.assertIn("unittest discover", workflow)
        self.assertIn("node --test", workflow)
        self.assertIn("validate_phased_docs.py", workflow)


if __name__ == "__main__":
    unittest.main()

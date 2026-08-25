from pathlib import Path
import shutil
import tempfile
import unittest

from tools.validate_project_agents import (
    EXPECTED_ROLES,
    discovered_names,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]


class ProjectAgentSuiteTest(unittest.TestCase):
    def test_complete_suite_passes_validator(self):
        self.assertEqual([], validate(ROOT))

    def test_expected_inventory_is_exact(self):
        self.assertEqual(set(EXPECTED_ROLES), discovered_names(ROOT))

    def test_validator_rejects_read_only_write_tool(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / ".codex", root / ".codex")
            path = root / ".codex/agents/email-project-manager.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace('"Bash"]', '"Bash", "Write"]', 1),
                encoding="utf-8",
            )
            self.assertTrue(
                any("read-only agent exposes write tools" in error for error in validate(root))
            )

    def test_validator_rejects_weak_external_operator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / ".codex", root / ".codex")
            path = root / ".codex/agents/shopify-messaging-campaign-operator.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace("explicit current-task approval", "owner permission", 1),
                encoding="utf-8",
            )
            self.assertTrue(
                any("explicit current-task approval" in error for error in validate(root))
            )

    def test_validator_rejects_active_mailerlite_instruction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / ".codex", root / ".codex")
            path = root / ".codex/agents/email-producer.md"
            path.write_text(
                path.read_text(encoding="utf-8") + "\ncreate a MailerLite campaign\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any("forbidden stale or unsafe text" in error for error in validate(root))
            )


if __name__ == "__main__":
    unittest.main()

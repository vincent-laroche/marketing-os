from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"


class GitHubTemplatesTest(unittest.TestCase):
    def test_all_governed_issue_forms_exist(self):
        expected = {"campaign.yml", "email.yml", "task.yml", "experiment.yml", "bug.yml", "config.yml"}
        self.assertEqual(expected, {path.name for path in TEMPLATES.glob("*.yml")})

    def test_forms_protect_pii_and_activation_boundary(self):
        for path in TEMPLATES.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            if path.name == "config.yml":
                continue
            with self.subTest(form=path.name):
                self.assertIn("customer PII", text)
                self.assertIn("does not authorize", text)

    def test_email_form_captures_shopify_readiness(self):
        text = (TEMPLATES / "email.yml").read_text(encoding="utf-8")
        for label in ("Execution Mode", "Messaging State", "Shopify Messaging URL", "Flow Required", "Flow State", "Shopify Flow URL", "Automation Trigger", "Automation / Flow Name"):
            self.assertIn(label, text)

    def test_pull_request_template_has_release_boundaries(self):
        text = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        for term in ("Closes #", "Relates to #", "Campaign", "Preview", "Creative QA", "Shopify Messaging", "Shopify Flow", "Consent", "Rollback"):
            self.assertIn(term, text)
        self.assertIn("Merge does not configure Shopify, schedule, activate, or send email", text)


if __name__ == "__main__":
    unittest.main()

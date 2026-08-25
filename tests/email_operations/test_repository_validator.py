import unittest

from pathlib import Path

from tools.github_campaign_os.validate_repository import ROOT, tracked_output_errors, validate, workflow_errors


class RepositoryValidatorTest(unittest.TestCase):
    def test_preview_publication_repository_contract_is_valid(self):
        self.assertEqual([], validate())

    def test_workflow_validator_rejects_trigger_and_permission_expansion(self):
        review = (ROOT / ".github/workflows/email-preview-review.yml").read_text(encoding="utf-8")
        publish = (ROOT / ".github/workflows/email-preview-publish.yml").read_text(encoding="utf-8")
        unsafe_trigger = publish.replace("  workflow_dispatch:", "  workflow_dispatch:\n  push:")
        self.assertTrue(any("trigger" in error for error in workflow_errors(review, unsafe_trigger)))
        unsafe_permission = publish.replace("      pages: write", "      pages: write\n      contents: write")
        self.assertTrue(any("permissions" in error for error in workflow_errors(review, unsafe_permission)))
        attacker = publish.replace("actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09", "attacker/backdoor@" + "a" * 40)
        self.assertTrue(any("action" in error for error in workflow_errors(review, attacker)))
        extra_job = publish + "\n  exfiltrate:\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n    steps: []\n"
        self.assertTrue(any("job set" in error for error in workflow_errors(review, extra_job)))
        quoted_permission = publish.replace("      pages: write", '      pages: write\n      "packages": write')
        self.assertTrue(any("mapping entry" in error for error in workflow_errors(review, quoted_permission)))

    def test_tracked_output_validator_rejects_public_evidence_and_binaries(self):
        self.assertEqual([], tracked_output_errors(["email-previews/publication-ledger.json"]))
        errors = tracked_output_errors(["email-previews/CR-1/rendered.html", "tools/email-preview/node_modules/playwright/browser.zip"])
        self.assertEqual(2, len(errors))


if __name__ == "__main__":
    unittest.main()

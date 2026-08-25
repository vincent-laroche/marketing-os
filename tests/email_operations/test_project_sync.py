import unittest

from tools.github_campaign_os.sync_project import KEY_RE, REPO, preview_url_clear_inputs, preview_url_readback_mismatches


class ProjectSyncTest(unittest.TestCase):
    def test_empty_ledger_derived_preview_url_is_explicitly_cleared(self):
        manifest = {"records": [
            {"key": "email:CR-1", "preview_url": None},
            {"key": "email:CR-2", "preview_url": "https://email-preview.hairsolutions.co/CR-2/detail.html"},
        ]}
        result = preview_url_clear_inputs("project-1", "preview", manifest, {"email:CR-1": "item-1", "email:CR-2": "item-2"})
        self.assertEqual([{"projectId": "project-1", "itemId": "item-1", "fieldId": "preview"}], result)

    def test_preview_url_readback_checks_exact_value_and_blank(self):
        manifest = {"records": [
            {"key": "email:CR-1", "preview_url": None},
            {"key": "email:CR-2", "preview_url": "https://email-preview.hairsolutions.co/CR-2/detail.html"},
        ]}
        project = {"items": {"nodes": [
            {"content": {"body": "<!-- campaign-os-key: email:CR-1 -->", "repository": {"nameWithOwner": REPO}}, "fieldValues": {"nodes": []}},
            {"content": {"body": "<!-- campaign-os-key: email:CR-2 -->", "repository": {"nameWithOwner": REPO}}, "fieldValues": {"nodes": [{"text": "https://email-preview.hairsolutions.co/CR-2/detail.html", "field": {"name": "Preview URL"}}]}},
        ]}}
        self.assertEqual([], preview_url_readback_mismatches(project, manifest))
        project["items"]["nodes"][1]["fieldValues"]["nodes"][0]["text"] = "https://wrong.example/"
        self.assertEqual("email:CR-2", preview_url_readback_mismatches(project, manifest)[0]["key"])

    def test_compiled_issue_marker_distinguishes_filed_tasks(self):
        self.assertIsNotNone(KEY_RE.search("<!-- campaign-os-key: email:CR-1 -->"))
        self.assertIsNone(KEY_RE.search("Calibration task without a compiled key"))


if __name__ == "__main__":
    unittest.main()

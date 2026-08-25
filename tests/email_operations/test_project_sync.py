import unittest

from tools.github_campaign_os.sync_project import preview_url_clear_inputs


class ProjectSyncTest(unittest.TestCase):
    def test_empty_ledger_derived_preview_url_is_explicitly_cleared(self):
        manifest = {"records": [
            {"key": "email:CR-1", "preview_url": None},
            {"key": "email:CR-2", "preview_url": "https://email-preview.hairsolutions.co/CR-2/detail.html"},
        ]}
        result = preview_url_clear_inputs("project-1", "preview", manifest, {"email:CR-1": "item-1", "email:CR-2": "item-2"})
        self.assertEqual([{"projectId": "project-1", "itemId": "item-1", "fieldId": "preview"}], result)


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "github-campaign-os" / "manifest.json"
SCHEMA = ROOT / "github-campaign-os" / "project-schema.json"


class CampaignOSManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_manifest_has_exact_canonical_inventory(self):
        records = self.manifest["records"]
        counts = {kind: sum(r["work_type"] == kind for r in records) for kind in ("Campaign", "Email", "Task", "Experiment", "Bug")}
        self.assertEqual({"Campaign": 7, "Email": 53, "Task": 8, "Experiment": 0, "Bug": 1}, counts)
        self.assertEqual(69, len({record["key"] for record in records}))

    def test_every_record_is_connector_readable_and_safe(self):
        for record in self.manifest["records"]:
            with self.subTest(key=record["key"]):
                self.assertIn(f'<!-- campaign-os-key: {record["key"]} -->', record["issue_body"])
                self.assertIn("<!-- campaign-os-snapshot:start -->", record["issue_body"])
                self.assertIn("<!-- campaign-os-snapshot:end -->", record["issue_body"])
                self.assertEqual(64, len(record["source_fingerprint"]))
                self.assertNotIn("/Users/", json.dumps(record))
                self.assertNotIn("@hairsolutions.co", record["issue_body"])

    def test_email_records_have_campaign_parents_and_sources(self):
        for record in self.manifest["records"]:
            if record["work_type"] != "Email":
                continue
            with self.subTest(key=record["key"]):
                self.assertTrue(record["parent_key"].startswith("campaign:"))
                self.assertTrue(any(path.startswith("shopify-messaging/emails/") for path in record["source_paths"]))
                self.assertEqual("Not Started", record["messaging_state"])

    def test_generated_files_are_reproducible_from_the_committed_tree(self):
        from tools.github_campaign_os.build_manifest import serialized

        for path, content in serialized().items():
            with self.subTest(generated=path.name):
                self.assertTrue(path.exists(), f"{path.name} is missing")
                self.assertEqual(
                    content,
                    path.read_text(encoding="utf-8"),
                    f"{path.name} is stale; run python3 -m tools.github_campaign_os.build_manifest --write",
                )

    def test_project_schema_has_28_fields_and_six_views(self):
        self.assertEqual("Email Marketing — Campaign OS", self.schema["title"])
        self.assertTrue(self.schema["private"])
        self.assertEqual(28, len(self.schema["fields"]))
        self.assertEqual(6, len(self.schema["views"]))
        self.assertEqual(28, len({field["name"] for field in self.schema["fields"]}))


if __name__ == "__main__":
    unittest.main()

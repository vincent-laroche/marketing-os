import unittest

from tools.github_campaign_os.preview_publications import merged_preview_urls, preview_urls


DIGEST = "a" * 64
SHA = "b" * 40
EXPECTED = {"CR-1": {"campaign_key": "campaign:J2", "source_path": "shopify-messaging/emails/01-cr-1.html", "canonical_issue": 10}}


def publication(**overrides):
    value = {
        "email_code": "CR-1", "campaign_key": "campaign:J2", "source_path": "shopify-messaging/emails/01-cr-1.html",
        "source_commit_sha": SHA, "canonical_issue": 10, "canonical_pr": 72, "persona": "normal-customer",
        "states": ["missing-first-name"], "output_sha256": {"rendered.html": DIGEST, "desktop.png": DIGEST, "mobile.png": DIGEST},
        "publication_timestamp": "2026-08-25T12:00:00Z", "canonical_url": "https://vincent-laroche.github.io/email-marketing-ops/CR-1/detail.html",
        "pages_deployment_id": "deploy-1", "workflow_run_id": "run-1", "workflow_attempt": "1",
    }
    value.update(overrides)
    return value


class PreviewPublicationTest(unittest.TestCase):
    def test_empty_ledger_produces_no_project_urls(self):
        self.assertEqual({}, preview_urls({"schema_version": 1, "publications": []}, EXPECTED, lambda entry: None))

    def test_verified_ledger_produces_exact_public_detail_url(self):
        result = preview_urls({"schema_version": 1, "publications": [publication()]}, EXPECTED, lambda entry: None)
        self.assertEqual("https://vincent-laroche.github.io/email-marketing-ops/CR-1/detail.html", result["CR-1"])

    def test_unmerged_append_stays_blank_and_merged_history_cannot_be_rewritten(self):
        empty = {"schema_version": 1, "publications": []}
        working = {"schema_version": 1, "publications": [publication()]}
        self.assertEqual({}, merged_preview_urls(working, empty, EXPECTED, lambda entry: None))
        with self.assertRaisesRegex(ValueError, "append-only history"):
            merged_preview_urls(empty, working, EXPECTED, lambda entry: None)
        mutated = {"schema_version": 1, "publications": [publication(canonical_pr=73)]}
        with self.assertRaisesRegex(ValueError, "append-only history"):
            merged_preview_urls(mutated, working, EXPECTED, lambda entry: None)

    def test_identity_url_digest_and_duplicate_drift_fail_closed(self):
        cases = [
            publication(canonical_issue=11),
            publication(canonical_pr=0),
            publication(canonical_url="https://evil.example/CR-1/detail.html"),
            publication(canonical_url="https://email-preview.hairsolutions.co/other/detail.html"),
            publication(output_sha256={"rendered.html": "bad", "desktop.png": DIGEST, "mobile.png": DIGEST}),
        ]
        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    preview_urls({"schema_version": 1, "publications": [candidate]}, EXPECTED, lambda entry: None)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            preview_urls({"schema_version": 1, "publications": [publication(), publication()]}, EXPECTED, lambda entry: None)


if __name__ == "__main__":
    unittest.main()

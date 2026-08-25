import unittest

from tools.github_campaign_os.preview_publications import merged_preview_urls, preview_urls


DIGEST = "a" * 64
SHA = "b" * 40
EXPECTED = {"CR-1": {"campaign_key": "campaign:J2", "source_path": "shopify-messaging/emails/01-cr-1.html", "canonical_issue": 10}}


def publication(**overrides):
    value = {
        "event": "published",
        "email_code": "CR-1", "campaign_key": "campaign:J2", "source_path": "shopify-messaging/emails/01-cr-1.html",
        "source_commit_sha": SHA, "canonical_issue": 10, "canonical_pr": 72, "persona": "normal-customer",
        "states": ["missing-first-name"], "output_sha256": {"rendered.html": DIGEST, "desktop.png": DIGEST, "mobile.png": DIGEST},
        "publication_timestamp": "2026-08-25T12:00:00Z", "canonical_url": "https://vincent-laroche.github.io/marketing-os/CR-1/detail.html",
        "pages_deployment_id": "deploy-1", "workflow_run_id": "run-1", "workflow_attempt": "1",
    }
    value.update(overrides)
    return value


def withdrawal(**overrides):
    value = {
        "event": "withdrawn", "email_code": "CR-1", "campaign_key": "campaign:J2",
        "source_path": "shopify-messaging/emails/01-cr-1.html", "source_commit_sha": "c" * 40,
        "canonical_issue": 10, "canonical_pr": 73, "publication_timestamp": "2026-08-25T13:00:00Z",
        "former_canonical_url": "https://vincent-laroche.github.io/marketing-os/CR-1/detail.html",
        "withdrawn_source_commit_sha": SHA, "withdrawn_pages_deployment_id": "deploy-1",
        "pages_deployment_id": "deploy-2", "workflow_run_id": "run-2", "workflow_attempt": "1",
        "reason": "owner-requested",
    }
    value.update(overrides)
    return value


class PreviewPublicationTest(unittest.TestCase):
    def test_empty_ledger_produces_no_project_urls(self):
        self.assertEqual({}, preview_urls({"schema_version": 2, "events": []}, EXPECTED, lambda entry: None))

    def test_verified_ledger_produces_exact_public_detail_url(self):
        result = preview_urls({"schema_version": 2, "events": [publication()]}, EXPECTED, lambda entry: None)
        self.assertEqual("https://vincent-laroche.github.io/marketing-os/CR-1/detail.html", result["CR-1"])

    def test_unmerged_append_stays_blank_and_merged_history_cannot_be_rewritten(self):
        empty = {"schema_version": 2, "events": []}
        working = {"schema_version": 2, "events": [publication()]}
        self.assertEqual({}, merged_preview_urls(working, empty, EXPECTED, lambda entry: None))
        with self.assertRaisesRegex(ValueError, "append-only history"):
            merged_preview_urls(empty, working, EXPECTED, lambda entry: None)
        mutated = {"schema_version": 2, "events": [publication(canonical_pr=73)]}
        with self.assertRaisesRegex(ValueError, "append-only history"):
            merged_preview_urls(mutated, working, EXPECTED, lambda entry: None)

    def test_only_the_exact_empty_v1_ledger_is_an_allowed_migration_baseline(self):
        working = {"schema_version": 2, "events": []}
        self.assertEqual({}, merged_preview_urls(working, {"schema_version": 1, "publications": []}, EXPECTED, lambda entry: None))
        with self.assertRaisesRegex(ValueError, "invalid publication ledger"):
            merged_preview_urls(working, {"schema_version": 1, "publications": [publication()]}, EXPECTED, lambda entry: None)

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
                    preview_urls({"schema_version": 2, "events": [candidate]}, EXPECTED, lambda entry: None)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            preview_urls({"schema_version": 2, "events": [publication(), publication()]}, EXPECTED, lambda entry: None)

    def test_merged_withdrawal_clears_url_but_unmerged_withdrawal_does_not(self):
        published = {"schema_version": 2, "events": [publication()]}
        withdrawn = {"schema_version": 2, "events": [publication(), withdrawal()]}
        self.assertIn("CR-1", merged_preview_urls(withdrawn, published, EXPECTED, lambda entry: None))
        self.assertEqual({}, merged_preview_urls(withdrawn, withdrawn, EXPECTED, lambda entry: None))
        with self.assertRaisesRegex(ValueError, "exact active"):
            preview_urls({"schema_version": 2, "events": [withdrawal()]}, EXPECTED, lambda entry: None)
        with self.assertRaisesRegex(ValueError, "exact active"):
            preview_urls({"schema_version": 2, "events": [publication(), withdrawal(withdrawn_source_commit_sha="e" * 40)]}, EXPECTED, lambda entry: None)

    def test_republication_requires_a_new_source_revision_and_restores_url(self):
        withdrawn = {"schema_version": 2, "events": [publication(), withdrawal()]}
        republished = publication(
            source_commit_sha="d" * 40,
            canonical_pr=84,
            publication_timestamp="2026-08-25T14:00:00Z",
            pages_deployment_id="deploy-3",
            workflow_run_id="run-3",
        )
        history = {"schema_version": 2, "events": [*withdrawn["events"], republished]}
        self.assertEqual(
            "https://vincent-laroche.github.io/marketing-os/CR-1/detail.html",
            preview_urls(history, EXPECTED, lambda entry: None)["CR-1"],
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            preview_urls({"schema_version": 2, "events": [publication(), withdrawal(), publication(publication_timestamp="2026-08-25T14:00:00Z")]}, EXPECTED, lambda entry: None)

    def test_timestamp_order_uses_instants_not_lexical_text(self):
        later = withdrawal(publication_timestamp="2026-08-25T12:00:00.123Z")
        self.assertEqual({}, preview_urls({"schema_version": 2, "events": [publication(), later]}, EXPECTED, lambda entry: None))
        earlier = withdrawal(publication_timestamp="2026-08-25T11:59:59.999Z")
        with self.assertRaisesRegex(ValueError, "append-ordered"):
            preview_urls({"schema_version": 2, "events": [publication(), earlier]}, EXPECTED, lambda entry: None)


if __name__ == "__main__":
    unittest.main()

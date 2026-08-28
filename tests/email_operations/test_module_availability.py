import json
from pathlib import Path
import unittest

from tools.github_campaign_os.module_availability import (
    ALIASES,
    VARIANTS,
    artifacts,
    build,
    complete,
    fold,
    requirements,
    resolve,
)

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "github-campaign-os" / "module-availability.json"


class ModuleAvailabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.availability = build()
        cls.available = complete(artifacts())
        cls.folded = {fold(label): label for label in cls.available}

    def test_every_approved_artifact_is_complete_in_both_variants(self):
        for label, entry in self.availability["artifacts"].items():
            with self.subTest(module=label):
                self.assertEqual(set(VARIANTS), set(entry["variants"]))
                self.assertEqual(64, len(entry["fingerprint"]))

    def test_folded_keys_never_collide(self):
        self.assertEqual(len(self.available), len({fold(label) for label in self.available}))

    def test_all_thirty_six_declared_module_blockers_resolve(self):
        emails = self.availability["emails"]
        self.assertEqual(36, len(emails))
        for email in emails:
            with self.subTest(email=email["email_code"]):
                self.assertEqual([], email["unresolved"])

    def test_resolution_modes_match_the_authoritative_audit(self):
        modes = {}
        for email in self.availability["emails"]:
            for entry in email["resolved"]:
                modes[entry["mode"]] = modes.get(entry["mode"], 0) + 1
        self.assertEqual({"exact-label": 74, "documented-alias": 11, "folded-label": 4}, modes)

    def test_grid_collections_four_resolves_only_by_punctuation_folding(self):
        artifact, mode = resolve("Grid - Collections 4", self.available, self.folded)
        self.assertEqual(("Grid - Collections (4)", "folded-label"), (artifact, mode))

    def test_documented_aliases_resolve_to_approved_artifacts(self):
        self.assertEqual({"Review stars", "Signal - Countdown"}, set(ALIASES))
        for declared, canonical in ALIASES.items():
            with self.subTest(alias=declared):
                self.assertEqual((canonical, "documented-alias"), resolve(declared, self.available, self.folded))

    def test_an_unavailable_module_stays_fail_closed(self):
        for absent in ("Hero - Nonexistent", "Grid - Collections (9)", "Totally Fake Module"):
            with self.subTest(module=absent):
                self.assertEqual((None, None), resolve(absent, self.available, self.folded))

    def test_requirements_split_on_every_documented_separator(self):
        self.assertEqual(["A", "B", "C", "D"], requirements("A, B; C | D"))
        self.assertEqual(["A", "B"], requirements("A\nB"))

    def test_generated_file_is_reproducible_from_the_committed_tree(self):
        self.assertTrue(GENERATED.exists())
        self.assertEqual(
            json.dumps(self.availability, ensure_ascii=False, indent=2) + "\n",
            GENERATED.read_text(encoding="utf-8"),
            "module-availability.json is stale; run python3 -m tools.github_campaign_os.build_manifest --write",
        )

    def test_email_codes_are_canonical_manifest_keys(self):
        manifest = json.loads((ROOT / "github-campaign-os" / "manifest.json").read_text(encoding="utf-8"))
        canonical = {r["key"].split(":", 1)[1] for r in manifest["records"] if r["work_type"] == "Email"}
        for email in self.availability["emails"]:
            with self.subTest(email=email["email_code"]):
                self.assertIn(email["email_code"], canonical)


if __name__ == "__main__":
    unittest.main()

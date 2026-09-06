"""The Proof Bank fill stage must resolve paths inside this repository.

It previously pointed at absolute paths under /Users/vMac/04_marketing/email_marketing, which
stopped existing when the repository was consolidated. The stage then did nothing, without
error, while build_emails.py produced newsletters with empty Proof Bank slots — the same
silent-wrong-output shape as #141, found while merging main during #145.

The pipeline is two stages. A test that only covers the first one cannot see this.
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "shopify-messaging" / "fill_proof_bank_nl.py"


class FillProofBankPathsTest(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists(), "the Proof Bank fill stage is missing")

    def test_no_absolute_paths_outside_the_repository(self):
        source = SCRIPT.read_text(encoding="utf-8")
        absolutes = [
            literal
            for literal in re.findall(r'"(/[^"\n]+)"', source)
            if not literal.startswith(str(ROOT))
        ]
        self.assertEqual(
            absolutes, [],
            f"{SCRIPT.name} hard-codes absolute paths that will not exist on another machine "
            f"or after a repository move: {absolutes}",
        )

    def test_resolved_paths_are_real(self):
        """Import the module and confirm the paths it derived actually exist."""
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("fill_proof_bank_nl", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        sys.modules["fill_proof_bank_nl"] = module
        # Importing runs the module's own fail-loud guard; a missing path raises SystemExit.
        spec.loader.exec_module(module)

        for name in ("EMAILS_DIR", "PROOF_BANK_JSON"):
            with self.subTest(constant=name):
                resolved = pathlib.Path(getattr(module, name))
                self.assertTrue(resolved.exists(), f"{name} resolves to a missing path: {resolved}")
                self.assertTrue(
                    str(resolved).startswith(str(ROOT)),
                    f"{name} resolves outside the repository: {resolved}",
                )


if __name__ == "__main__":
    unittest.main()

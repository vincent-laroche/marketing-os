"""The builder must reproduce the committed emails.

This test exists because it did not, and nothing noticed. Between 2026-08-24 and 2026-09-05
`tools/build53/build_emails.py` silently regressed every email it regenerated: it dropped the
J2 abandoned-checkout Liquid loop, double-escaped richtext into a visible `&lt;p&gt;`, and
inserted a duplicate CTA. The builder still reported `51 GREEN 2 BLOCKED 0 ISSUES` over that
output, and the only reproducibility test in the suite covered `github-campaign-os/manifest.json`
rather than the emails (#141).

`shopify-messaging/J2-CART-RECOVERY-READY.md` asked whether CR-1..CR-4 should keep their
hand-edits or return to the Email Reference File module palette. **Vincent decided 2026-09-05:
return to the palette.** All 53 emails are therefore builder output, and `KNOWN_DIVERGENT` is
empty. A file appearing there again means someone hand-edited output instead of fixing source.
"""

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILDER = ROOT / "tools" / "build53" / "build_emails.py"
COMMITTED = ROOT / "shopify-messaging" / "emails"

# Empty by decision (2026-09-05): every email is builder output. Adding an entry here means
# accepting a hand-edit that source cannot reproduce — which is what let a regression hide for
# twelve days. Fix the deck or the builder instead.
KNOWN_DIVERGENT: set[str] = set()


class Build53ReproducibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        env = {**os.environ, "BUILD53_OUT_DIR": cls._tmp.name}
        proc = subprocess.run(
            [sys.executable, str(BUILDER)],
            cwd=str(ROOT), env=env, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise AssertionError(f"builder failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
        cls.built = pathlib.Path(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_builder_reproduces_every_committed_email(self):
        committed = sorted(p.name for p in COMMITTED.glob("*.html"))
        self.assertTrue(committed, "no committed emails found")

        for name in committed:
            with self.subTest(email=name):
                rebuilt = self.built / name
                self.assertTrue(rebuilt.exists(), f"{name} was not produced by the builder")
                a = (COMMITTED / name).read_text(encoding="utf-8")
                b = rebuilt.read_text(encoding="utf-8")
                if name in KNOWN_DIVERGENT:
                    continue
                self.assertEqual(
                    a, b,
                    f"{name} does not match the builder's output. Either the committed file was "
                    f"hand-edited without updating tools/build53/build_emails.py, or the builder "
                    f"regressed. Do not resolve this by committing the rebuild without reading "
                    f"the diff — see #141.",
                )

    def test_known_divergences_are_still_real(self):
        """A stale exception is as dangerous as a missing one."""
        for name in sorted(KNOWN_DIVERGENT):
            with self.subTest(email=name):
                a = (COMMITTED / name).read_text(encoding="utf-8")
                b = (self.built / name).read_text(encoding="utf-8")
                self.assertNotEqual(
                    a, b,
                    f"{name} now rebuilds identically, so it is no longer a divergence. "
                    f"Remove it from KNOWN_DIVERGENT.",
                )

    def test_no_email_renders_escaped_markup(self):
        """#142: richtext defaults were escaped, printing literal <p> in the footer."""
        for path in sorted(COMMITTED.glob("*.html")):
            with self.subTest(email=path.name):
                body = path.read_text(encoding="utf-8")
                self.assertNotIn(
                    "&lt;p&gt;", body,
                    f"{path.name} contains an escaped <p>, which renders as visible markup "
                    f"in the compliance footer (#142).",
                )


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
EMAILS = tuple(sorted((ROOT / "shopify-messaging" / "emails").glob("0[1-4]-cr-*.html")))
APPROVED = {"#f6efd9", "#ede3cc", "#151411", "#25221d", "#c7bfac", "#ea6452"}
SUPERSEDED = {"#f7f1de", "#efe7d2", "#15140f", "#2a2620", "#ddd2b6", "#ed6f5c"}


class J2EmailContractTest(unittest.TestCase):
    def test_all_four_cart_recovery_emails_are_present(self):
        self.assertEqual(4, len(EMAILS))

    def test_palette_and_transparent_page_contract(self):
        for path in EMAILS:
            with self.subTest(email=path.name):
                html = path.read_text(encoding="utf-8")
                colors = {value.lower() for value in re.findall(r"#[0-9A-Fa-f]{6}", html)}
                self.assertFalse(colors & SUPERSEDED, colors & SUPERSEDED)
                self.assertTrue(colors <= APPROVED, colors - APPROVED)
                self.assertIn('body style="margin:0;padding:0;background-color:transparent;"', html)
                self.assertRegex(
                    html,
                    r'<table[^>]+width="100%"[^>]+background-color:transparent',
                )

    def test_shopify_liquid_compliance_and_image_contract(self):
        for path in EMAILS:
            with self.subTest(email=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("abandoned_checkout.line_items", html)
                self.assertIn("{{ unsubscribe_url }}", html)
                self.assertIn("Ehitajate tee 110", html)
                for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
                    self.assertTrue(src.startswith("https://"), src)


if __name__ == "__main__":
    unittest.main()

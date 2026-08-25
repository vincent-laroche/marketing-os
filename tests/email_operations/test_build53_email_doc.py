import unittest

from tools.build53.build_emails import email_doc


class Build53EmailDocTest(unittest.TestCase):
    def test_build_note_merge_tags_are_translated_before_escaping(self):
        row = {"Email name": "PP-7 · Test", "Preview Text": ""}

        document = email_doc(row, ["Hi {{ firstname }},"], [], {})

        self.assertIn(
            '<!-- BUILD NOTE: Hi {{ customer.first_name | default: "there" }}, -->',
            document,
        )
        self.assertNotIn("{{ firstname }}", document)


if __name__ == "__main__":
    unittest.main()

import unittest

from tools.github_campaign_os.validate_repository import validate


class RepositoryValidatorTest(unittest.TestCase):
    def test_preview_publication_repository_contract_is_valid(self):
        self.assertEqual([], validate())


if __name__ == "__main__":
    unittest.main()

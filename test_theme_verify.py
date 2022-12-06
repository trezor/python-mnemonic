import unittest
from pathlib import Path
from mnscripts.themes.theme_verify import load_file, ThemeDict, Verifier, VerificationFailed


class VerifierTestCase(unittest.TestCase):
    def _load_test_file(self):
        """
            Load the template file to run the tests
        """
        file_name = "test_verifier"
        test_path = Path("edit_themes") / Path("theme_test")
        self.test_file = load_file(file_name, test_path)

    def test_start_verification(self):
        """
            Test the verification successes
        """
        self._load_test_file()
        theme_to_verify = ThemeDict(self.test_file)
        verifier = Verifier()
        verifier.set_verify_file(theme_to_verify)
        verifier.start_verification()
        self.assertTrue(verifier.validated)

    def test_verification_fail(self):
        """
            Test the verification failures
        """
        self._load_test_file()
        theme_to_verify = ThemeDict(self.test_file)
        verifier = Verifier()
        verifier.set_verify_file(theme_to_verify)

        for each_key, each_value in self.test_file.items():
            theme_with_fail = ThemeDict(self.test_file["main_test_ok"])
            if each_key == "main_test_ok":
                continue
            theme_with_fail.update(each_value)
            verifier.set_verify_file(theme_with_fail)
            with self.assertRaises(VerificationFailed):
                verifier.start_verification()


if __name__ == '__main__':
    unittest.main()

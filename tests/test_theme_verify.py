import unittest
import json
from pathlib import Path
from src.mnemonic.mnemonic import ThemeDict, Verifier, VerificationFailed


class VerifierTestCase(unittest.TestCase):
    def _load_test_file(self):
        """
            Load the template file to run the tests
        """

        test_file = Path(__file__).parent.absolute() / Path("theme_test") / Path("test_verifier.json")
        if Path.exists(test_file) and Path.is_file(test_file):
            with open(test_file) as json_file:
                self.test_file = ThemeDict(json.load(json_file))
        else:
            raise FileNotFoundError("Theme file not found")

    def test_start_verification(self):
        """
            Test the verification successes
        """
        self._load_test_file()
        theme_to_verify = ThemeDict(self.test_file)
        verifier = Verifier()
        verifier.set_verify_theme(theme_to_verify)
        verifier.start_verification()
        self.assertTrue(verifier.validated)

    def test_verification_fail(self):
        """
            Test the verification failures
        """
        self._load_test_file()
        theme_to_verify = ThemeDict(self.test_file)
        verifier = Verifier()
        verifier.set_verify_theme(theme_to_verify)

        for each_key, each_value in self.test_file.items():
            theme_with_fail = ThemeDict(self.test_file["main_test_ok"])
            if each_key == "main_test_ok":
                continue
            theme_with_fail.update(each_value)
            verifier.set_verify_theme(theme_with_fail)
            with self.assertRaises(VerificationFailed):
                verifier.start_verification()


if __name__ == '__main__':
    unittest.main()

import unittest
import json
from pathlib import Path
from src.mnemonic.mnemonic import ThemeDict, Mnemonic


class VerificationFailed(Exception):
    pass


class Verifier:
    DEFAULT_THEME = "BIP39"

    def __init__(self, theme_name: str = ""):
        self.is_bip39 = theme_name.startswith(self.DEFAULT_THEME)
        self.theme_loaded = ThemeDict()
        self.current_word = ""
        self.current_restriction = ""
        self.validated = False

    @property
    def next_dictionary(self) -> ThemeDict:
        """ The dictionary of the current led syntactic word"""
        next_dictionary = ThemeDict(self.theme_loaded[self.current_restriction]) \
            if self.current_restriction in self.theme_loaded.keys() else ThemeDict()
        return next_dictionary

    @property
    def current_dict(self) -> ThemeDict:
        """ The dictionary of the current evaluated syntactic word"""
        current_dict = ThemeDict(self.theme_loaded[self.current_word]) \
            if self.current_word in self.theme_loaded.keys() else ThemeDict()
        return current_dict

    @property
    def led_words(self) -> ThemeDict:
        """ The mapped words of the current dictionary"""
        led_words = ThemeDict(self.current_dict[self.current_restriction]) \
            if self.current_restriction in self.current_dict.keys() else ThemeDict()
        return led_words

    def set_verify_theme(self, theme_loaded: ThemeDict):
        """ Set the dictionary to be verified"""
        self.theme_loaded = theme_loaded

    def start_verification(self):
        """
            Check all verifications in the lists and
            keys of the dictionary according to the Formosa standard
        """
        for filling_order_word in self.theme_loaded.filling_order:
            self.current_word = filling_order_word

            self.check_filling_sequence()
            self.check_restriction_sequence()
            self.check_total_words()

            for current_restriction in self.current_dict.leads:
                self.current_restriction = current_restriction

                self.check_image_list()
                self.check_keys_list()
                self.check_enough_sublists()
                self.check_mapping_consistence()
                self.check_space_char_general()

        self.validated = True

    def check_filling_sequence(self):
        """ Verify if the filling order has a consistence sequence with restriction sequence"""
        restrict_by = self.current_dict.led_by
        filling_order = self.theme_loaded.filling_order
        if restrict_by == "NONE":
            return
        if not {restrict_by, self.current_word}.issubset(filling_order):
            error_message = "The filling order list is incomplete."
            raise VerificationFailed(error_message)
        if not filling_order.index(restrict_by) < filling_order.index(self.current_word):
            error_message = "List sequence has inconsistent restriction order for %s and %s."
            raise VerificationFailed(error_message % (restrict_by, self.current_word))

    def check_restriction_sequence(self):
        """ Verify if the restriction has a consistence sequence"""
        filling_order = self.theme_loaded.filling_order
        if any([filling_order.index(each_restriction) >= filling_order.index(each_next_restriction)
                for each_restriction in self.current_dict.leads
                for each_next_restriction in self.theme_loaded[each_restriction].leads]):
            error_message = "List sequence inconsistent restriction order for %s."
            raise VerificationFailed(error_message % self.current_word)

    def check_total_words(self):
        """ Verify if the total words has enough words"""
        bits_length = 2 ** self.current_dict.bit_length
        total_words = self.current_dict.total_words
        if len(total_words) < bits_length:
            error_message = "The total words of %s are not enough for the theme, " \
                            "it should have %d words but it has %d words."
            raise VerificationFailed(error_message % (self.current_word.lower(), bits_length, len(total_words)))

    def check_image_list(self):
        """ Verify if image contains all mapped words"""
        all_keys = {next_restriction: self.next_dictionary[next_restriction].mapping.keys()
                    for next_restriction in self.next_dictionary.leads}
        if not all([image_word in each_restriction
                    for image_word in self.led_words.image
                    for each_restriction in all_keys.values()]):
            error_message = "A word from the image list of %s led by " \
                            "%s is not contained in the mapping keys list"
            raise VerificationFailed(error_message % (self.current_restriction, self.current_word))

    def check_keys_list(self):
        """ Verify if all keys are within in the total lists"""
        if not all([each_map_key in self.current_dict.total_words
                    for each_map_key in self.led_words.mapping.keys()]):
            error_message = "All keys should be listed in totals, but it is not, " \
                            "a key in dictionary of %s is not in total of %s keys."
            raise VerificationFailed(error_message % (self.current_restriction, self.current_word))

    def check_enough_sublists(self):
        """ Verify the amount of mapping keys"""
        mapping_size = len(self.led_words.mapping.keys())
        bits_length = 2 ** self.current_dict.bit_length
        if not mapping_size >= bits_length:
            error_message = "The dictionary of %s should contain %d keys words in %s list, " \
                            "but it contains %d keys words."
            raise VerificationFailed(error_message % (self.current_word,
                                                      bits_length,
                                                      self.current_restriction,
                                                      mapping_size))

    def check_mapping_consistence(self):
        """ Verify for each mapping word the amount of mapping keys and length of mapped list"""
        # The length of the lists must be two raised to the number of bits
        line_bits_length = 2 ** self.next_dictionary.bit_length
        # Check for each line in the keys list
        for mapping_key in self.led_words.mapping.keys():
            self._check_enough_keys(mapping_key, line_bits_length)
            self._check_complete_list(mapping_key)
            self._check_space_char_specific(mapping_key)
        self.check_general_unicity()

    def _check_enough_keys(self, mapping_key: list[str], line_bits_length: int):
        """
            Verify if the list of mapped keys has the correct length of words
        Parameters
        ----------
        mapping_key : list[str]
            The list of mapped keys
        line_bits_length : int
            The length of the list of mapped words
        """
        # Remove duplicates with dict.fromkeys(x)
        list_length = len(dict.fromkeys(self.led_words.mapping[mapping_key]))
        # Check whether length has correct value
        if list_length != line_bits_length:
            error_message = "Key %s, in %s restriction, should contain %d words, but it contains %d words."
            raise VerificationFailed(error_message % (mapping_key, self.current_restriction,
                                                      line_bits_length, list_length))

    def _check_alphabetically_order(self,  mapping_key: list[str]):
        mapped_words = self.led_words.mapping[mapping_key]
        if mapped_words != sorted(mapped_words):
            error_message = "The list of mapped words of %s, in %s restriction, is not alphabetically ordered"
            raise VerificationFailed(error_message % (mapping_key, self.current_restriction))

    def _check_complete_list(self, mapping_key: list[str]):
        """
            Verify if the complete list is actually complete
        Parameters
        ----------
        mapping_key : list[str]
            The list of mapped keys
        """
        if any([word not in self.next_dictionary.total_words
                for word in self.led_words.mapping[mapping_key]]):
            error_message = "A word from %s dictionary is not found in list of total words in %s."
            raise VerificationFailed(error_message % (self.current_word, self.current_restriction))

    def check_space_char_general(self):
        """ Check if there is any space character in the general lists Total Words, Mapping keys and Image words"""
        space_in_total_words = " " in "".join(self.current_dict.total_words)
        space_in_images = " " in "".join(self.current_dict[self.current_restriction].image)
        space_in_keys = " " in "".join(self.current_dict[self.current_restriction].mapping.keys())

        if space_in_total_words or space_in_images or space_in_keys:
            error_message = "Space character found in %s"
            raise VerificationFailed(error_message % self.current_word.lower())

    def _check_space_char_specific(self, mapping_key: list[str]):
        """
            Check if there is any space character in the sublists of each key word
        Parameters
        ----------
        mapping_key : list[str]
            The list of mapped keys
        """
        sublists = self.led_words.mapping[mapping_key]
        space_in_sublist = " " in "".join(sublists)
        if space_in_sublist:
            error_message = "Space character found in sublist of %s %s"
            raise VerificationFailed(error_message % (self.current_word.lower(), mapping_key))

    def check_general_unicity(self):
        """
            Check the theme unicity
            The unicity means the words in the same list should have the unique first letters
        """
        if self.current_word in self.theme_loaded.prime_syntactic_leads:
            sublist = self.theme_loaded[self.current_word].total_words
            self.check_list_unicity(sublist)

        for mapping_key in self.led_words.mapping.keys():
            sublist = self.led_words.mapping[mapping_key]
            self.check_list_unicity(sublist)

    def check_list_unicity(self, sublist: list[str]):
        """
            Check the unicity in a given list of words with the difference of list and set sizes

        Parameters
        ----------
        sublist : list[str]
            The list of led words which should have the letters unicity
        """
        # Concatenate the first n letters of each word in a set
        # If the word in BIP39 has 3 letters finish with "-"
        n = 4 if self.is_bip39 else 2
        unique_list = set([w[:n] if len(w) >= n else w+"-" for w in sublist])
        if len(unique_list) != len(sublist) and len(sublist):
            error_message = "The list of %s in the %s has no unicity."
            raise VerificationFailed(
                error_message % (self.current_restriction.lower()+"s", self.current_word.lower())
            )


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

    def test_themes(self):
        """
            Find and test all themes with the Verifier object
        """
        themes = Mnemonic.find_themes()
        for each_theme in themes:
            self._check_list(each_theme)

    def _check_list(self, theme: str):
        """
            For each found theme test it with the Verifier

        Parameters
        ----------
        theme : str
            The name of the theme to be verified
        """
        root_path = Path(__file__).parent.parent.absolute()
        themes_path = Path("src") / Path("mnemonic") / Path("themes")
        theme_file = root_path / themes_path / Path(theme + ".json")

        if Path.exists(theme_file) and Path.is_file(theme_file):
            with open(theme_file) as json_file:
                self.words_dictionary = ThemeDict(json.load(json_file))
        else:
            raise FileNotFoundError("Theme file not found")
        verifier = Verifier(theme)
        verifier.set_verify_theme(self.words_dictionary)
        verifier.start_verification()


def __main__() -> None:
    unittest.main()


if __name__ == "__main__":
    __main__()

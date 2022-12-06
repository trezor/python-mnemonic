
import json
import sys
from pathlib import Path

# This prevents IDE from creating a cache file
sys.dont_write_bytecode = True


class VerificationFailed(Exception):
    pass


class ThemeDict(dict):
    """
        This class inherits builtin dict and facilitate the access to structural keys
        mitigating issues with string references
    """
    FILL_SEQUENCE_KEY = "FILLING_ORDER"
    NATURAL_SEQUENCE_KEY = "NATURAL_ORDER"
    RESTRICTS_KW = "RESTRICTS"
    RESTRICTED_KW = "RESTRICTED_BY"
    TOTALS_KW = "TOTAL_LIST"
    IMAGE_KW = "IMAGE"
    MAPPING_KW = "MAPPING"
    BITS_KW = "BIT_LENGTH"

    def __init__(self, mapping=None):
        mapping = {} if mapping is None else mapping
        self.inner_dict = mapping
        if isinstance(mapping, ThemeDict):
            self.inner_dict = mapping.inner_dict
            super().__init__(self.inner_dict)
        else:
            super().__init__(mapping)

        self.version = ""

    def __getitem__(self, item):
        """
            Overloads __getitem__ from dict to return ThemeDict type when the returned item is a dict
            Work as dict.__getitem__ in all other ways
        """
        ret = dict.__getitem__(self, item)
        ret = ThemeDict(ret) if isinstance(ret, dict) else ret
        return ret

    def __setitem__(self, key, value):
        """
            Overloads __setitem__ from dict to set ThemeDict type when the set item is a dict
            Work as dict.__setitem__ in all other ways
        """
        dict.__setitem__(self, key, ThemeDict(value)) \
            if isinstance(value, dict) else dict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        """
            Overloads update from dict to call this class overloaded methods
        """
        for k, v in ThemeDict(*args, **kwargs).items():
            self[k] = v

    @property
    def filling_order(self) -> list[str]:
        """
            The list of words in restriction sequence to form a sentence
        """
        filling_order = self[self.FILL_SEQUENCE_KEY] if self.FILL_SEQUENCE_KEY in self.keys() else []
        return filling_order

    @property
    def natural_order(self) -> list[str]:
        """
            The list of words in natural speech to form a sentence
        """
        natural_order = self[self.NATURAL_SEQUENCE_KEY] if self.NATURAL_SEQUENCE_KEY in self.keys() else []
        return natural_order

    @property
    def restricts(self) -> list:
        """
            The list of words restricted by this dictionary
        """
        restricts = self[self.RESTRICTS_KW] if self.RESTRICTS_KW in self.keys() else []
        return restricts

    @property
    def total_words(self) -> list:
        """
            The list of all words of this syntactic word
        """
        total_words = self[self.TOTALS_KW] if self.TOTALS_KW in self.keys() else []
        return total_words

    @property
    def image(self) -> list:
        """
            The list of all words restricted by this syntactic word
        """
        image = self[self.IMAGE_KW] if self.IMAGE_KW in self.keys() else []
        return image

    @property
    def mapping(self) -> 'ThemeDict':
        """
            The list of all words restricted by this syntactic word
        """
        mapping = ThemeDict(self[self.MAPPING_KW]) if self.MAPPING_KW in self.keys() else ThemeDict()
        return mapping

    @property
    def bit_length(self) -> int:
        """
            The number of bits to map the words
        """
        bit_length = self[self.BITS_KW] if self.BITS_KW in self.keys() else 0
        return bit_length

    @property
    def restricted_by(self) -> str:
        """
            The word that restricts this dictionary
        """
        restricted_by = self[self.RESTRICTED_KW] if self.RESTRICTED_KW in self.keys() else ""
        return restricted_by

    @property
    def bits_per_phrase(self) -> int:
        """
            Bits mapped by each phrase in this theme
        """
        bits_per_phrase = sum([self[syntactic_word].bit_length for syntactic_word in self.filling_order])
        return bits_per_phrase

    @property
    def words_per_phrase(self) -> int:
        """
            Words mapping in each phrase in this theme
        """
        words_per_phrase = len(self.filling_order)
        assert words_per_phrase == len(self.natural_order)
        return words_per_phrase


class Verifier:
    def __init__(self):
        self.theme_loaded = ThemeDict()
        self.current_word = ""
        self.current_restriction = ""
        self.validated = False

    @property
    def next_dictionary(self) -> ThemeDict:
        """
            The dictionary of the current restricted syntactic word
        """
        next_dictionary = ThemeDict(self.theme_loaded[self.current_restriction]) \
            if self.current_restriction in self.theme_loaded.keys() else ThemeDict()
        return next_dictionary

    @property
    def current_dict(self) -> ThemeDict:
        """
            The dictionary of the current evaluated syntactic word
        """
        current_dict = ThemeDict(self.theme_loaded[self.current_word]) \
            if self.current_word in self.theme_loaded.keys() else ThemeDict()
        return current_dict

    @property
    def restricted_words(self) -> ThemeDict:
        """
            The mapped words of the current dictionary
        """
        restricted_words = ThemeDict(self.current_dict[self.current_restriction]) \
            if self.current_restriction in self.current_dict.keys() else ThemeDict()
        return restricted_words

    def set_verify_file(self, theme_loaded: ThemeDict):
        """
            Set the dictionary to be verified
        """
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

            for current_restriction in self.current_dict.restricts:
                self.current_restriction = current_restriction

                self.check_image_list()
                self.check_keys_list()
                self.check_enough_sublists()
                self.check_mapping_consistence()
                self.check_space_char_general()

        self.validated = True

    def check_filling_sequence(self):
        """
            Verify if the filling order has a consistence sequence with restriction sequence
        """
        restrict_by = self.current_dict.restricted_by
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
        """
            Verify if the restriction has a consistence sequence
        """
        filling_order = self.theme_loaded.filling_order
        if any([filling_order.index(each_restriction) >= filling_order.index(each_next_restriction)
                for each_restriction in self.current_dict.restricts
                for each_next_restriction in self.theme_loaded[each_restriction].restricts]):
            error_message = "List sequence inconsistent restriction order for %s."
            raise VerificationFailed(error_message % self.current_word)

    def check_image_list(self):
        """
            Verify if image contains all mapped words
        """
        all_keys = {next_restriction: self.next_dictionary[next_restriction].mapping.keys()
                    for next_restriction in self.next_dictionary.restricts}
        if not all([image_word in each_restriction
                    for image_word in self.restricted_words.image
                    for each_restriction in all_keys.values()]):
            error_message = "A word from the image list of %s restricted by " \
                            "%s is not contained in the mapping keys list"
            raise VerificationFailed(error_message % (self.current_restriction, self.current_word))

    def check_keys_list(self):
        """
            Verify if all keys are within in the total lists
        """
        if not all([each_map_key in self.current_dict.total_words
                    for each_map_key in self.restricted_words.mapping.keys()]):
            error_message = "All keys should be listed in totals, but it is not, "\
                            "a key in dictionary of %s is not in total of %s keys."
            raise VerificationFailed(error_message % (self.current_restriction, self.current_word))

    def check_enough_sublists(self):
        """
            Verify the amount of mapping keys
        """
        mapping_size = len(self.restricted_words.mapping.keys())
        bits_length = 2 ** self.current_dict.bit_length
        if not mapping_size >= bits_length:
            error_message = "The dictionary of %s should contain %d keys words in %s list, " \
                            "but it contains %d keys words."
            raise VerificationFailed(error_message % (self.current_word,
                                                      bits_length,
                                                      self.current_restriction,
                                                      mapping_size))

    def check_mapping_consistence(self):
        """
            Verify for each mapping word the amount of mapping keys and length of mapped list
        """
        # The length of the lists must be two raised to the number of bits
        line_bits_length = 2 ** self.next_dictionary.bit_length
        # Check for each line in the keys list
        for mapping_key in self.restricted_words.mapping.keys():
            self._check_enough_keys(mapping_key, line_bits_length)
            self._check_complete_list(mapping_key)
            self._check_space_char_specific(mapping_key)

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
        list_length = len(dict.fromkeys(self.restricted_words.mapping[mapping_key]))
        # Check whether length has correct value
        if list_length != line_bits_length:
            error_message = "Key %s, in %s restriction, should contain %d words, but it contains %d words."
            raise VerificationFailed(error_message % (mapping_key, self.current_restriction,
                                                      line_bits_length, list_length))

    def _check_alphabetically_order(self,  mapping_key: list[str]):
        mapped_words = self.restricted_words.mapping[mapping_key]
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
                for word in self.restricted_words.mapping[mapping_key]]):
            error_message = "A word from %s dictionary is not found in list of total words in %s."
            raise VerificationFailed(error_message % (self.current_word, self.current_restriction))

    def check_space_char_general(self):
        """
            Check if there is any space character in the general lists Total Words, Mapping keys and Image words
        """
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
        sublists = self.restricted_words.mapping[mapping_key]
        space_in_sublist = " " in "".join(sublists)
        if space_in_sublist:
            error_message = "Space character found in sublist of %s %s"
            raise VerificationFailed(error_message % (self.current_word.lower(), mapping_key))


def load_file(theme_name: str, folder_path: Path) -> dict:
    """
        Load the json file to a dictionary with a given theme

    Parameters
    ----------
    theme_name : str
        The name of the theme to be loaded
    folder_path : Path
        The path of the folder which the theme file is located

    Returns
    -------
    dict
        The dictionary with the words with Formosa standard
    """
    mnemonic_path = Path(__file__).parent.parent.absolute()
    complete_path = mnemonic_path / folder_path / ("%s.json" % theme_name)
    with open(complete_path) as json_file:
        words_dictionary = json.load(json_file)
    return words_dictionary


if __name__ == '__main__':
    if len(sys.argv) == 2:
        theme = sys.argv[1]
        test_path = Path("themes")
        test_file = load_file(theme, test_path)
        print("Start verification of theme", theme)
        theme_to_verify = ThemeDict(test_file)
        verifier = Verifier()
        verifier.set_verify_file(theme_to_verify)
        verifier.start_verification()
        assert verifier.validated
        print("Verified theme ", theme, ", OK", sep='')

#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import hashlib
import hmac
import itertools
import json
import sys
import unicodedata
from pathlib import Path
from typing import TypeVar, Union

# This prevents IDE from creating a cache file
sys.dont_write_bytecode = True
_T = TypeVar("_T")
PBKDF2_ROUNDS = 2048


class ConfigurationError(Exception):
    pass


class ThemeAmbiguous(Exception):
    pass


class ThemeNotFound(Exception):
    pass


class ThemeDict(dict):
    """
        This class inherits builtin dict and facilitate the access to structural keys
        mitigating issues with string references
    """
    FILL_SEQUENCE_KEY = "FILLING_ORDER"
    NATURAL_SEQUENCE_KEY = "NATURAL_ORDER"
    LEADS_KW = "LEADS"
    LED_KW = "LED_BY"
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
        """ Overloads update from dict to call this class overloaded methods"""
        for k, v in ThemeDict(*args, **kwargs).items():
            self[k] = v

    @property
    def filling_order(self) -> list[str]:
        """ The list of words in restriction sequence to form a sentence"""
        filling_order = self[self.FILL_SEQUENCE_KEY] if self.FILL_SEQUENCE_KEY in self.keys() else []
        return filling_order

    @property
    def natural_order(self) -> list[str]:
        """ The list of words in natural speech to form a sentence"""
        natural_order = self[self.NATURAL_SEQUENCE_KEY] if self.NATURAL_SEQUENCE_KEY in self.keys() else []
        return natural_order

    @property
    def leads(self) -> list:
        """ The list of words led by this dictionary"""
        leads = self[self.LEADS_KW] if self.LEADS_KW in self.keys() else []
        return leads

    @property
    def total_words(self) -> list:
        """ The list of all words of this syntactic word"""
        total_words = self[self.TOTALS_KW] if self.TOTALS_KW in self.keys() else []
        return total_words

    @property
    def image(self) -> list:
        """ The list of all words led by current syntactic word"""
        image = self[self.IMAGE_KW] if self.IMAGE_KW in self.keys() else []
        return image

    @property
    def mapping(self) -> 'ThemeDict':
        """ The list of all words led by this syntactic word"""
        mapping = ThemeDict(self[self.MAPPING_KW]) if self.MAPPING_KW in self.keys() else ThemeDict()
        return mapping

    @property
    def bit_length(self) -> int:
        """ The number of bits to map the words"""
        bit_length = self[self.BITS_KW] if self.BITS_KW in self.keys() else 0
        return bit_length

    @property
    def led_by(self) -> str:
        """ The word that leads this dictionary"""
        led_by = self[self.LED_KW] if self.LED_KW in self.keys() else ""
        return led_by

    def get_led_by_mapping(self, led_by: str) -> 'ThemeDict':
        """
            Get the mapping of the leading word

        Parameters
        ----------
        led_by : str
            The leading word to get the mapping from

        Returns
        -------
        ThemeDict
            The dict with the mapping lists of words
        """
        syntactic_leads = self[led_by].led_by
        led_by_mapping = self[syntactic_leads][led_by].mapping
        return led_by_mapping

    @property
    def bits_per_phrase(self) -> int:
        """ Bits mapped by each phrase in this theme"""
        bits_per_phrase = sum([self[syntactic_word].bit_length for syntactic_word in self.filling_order])
        return bits_per_phrase

    @property
    def bits_fill_sequence(self) -> list[int]:
        """ The bit length of the word in the filling order"""
        bit_sequence = [self[each_word].bit_length for each_word in self.filling_order]
        return bit_sequence

    @property
    def words_per_phrase(self) -> int:
        """ Words mapping in each phrase in this theme"""
        words_per_phrase = len(self.filling_order)
        if words_per_phrase != len(self.natural_order):
            error_message = "The theme is malformed"
            raise Exception(error_message)
        return words_per_phrase

    @property
    def wordlist(self) -> list[str]:
        """ All words used in the theme"""
        # Remove duplicates with list(dict.fromkeys(x)), concatenate all lists with itertools.chain.from_iterable(y)
        wordlist = list(dict.fromkeys(itertools.chain.from_iterable(
            self[each_fill_word].total_words
            for each_fill_word in self.filling_order
            if each_fill_word in self.keys())))
        return wordlist

    @property
    def restriction_sequence(self) -> list[tuple[str, str]]:
        """ The list of restrictions used in this theme"""
        restriction_sequence = [(syntactic_word, each_restriction)
                                for syntactic_word in self.filling_order
                                for each_restriction in self[syntactic_word].leads]
        return restriction_sequence

    def natural_index(self, syntactic_word: str) -> int:
        """
            Give the sentence index in the natural speech of a given syntactic word

        Parameters
        ----------
        syntactic_word : str
            The word given to find the index in the sentence

        Returns
        -------
        int
            The index of the word given in the natural speech of the sentence
        """
        natural_index = self.natural_order.index(syntactic_word)
        return natural_index

    @property
    def natural_map(self) -> list[int]:
        """ The mapping of indexes of the natural order in the filling order"""
        natural_map = list(map(self.natural_index, self.filling_order))
        return natural_map

    @property
    def filling_map(self) -> list[int]:
        """ The mapping of indexes of the filling order in the natural order"""
        filling_map = list(map(self.fill_index, self.natural_order))
        return filling_map

    @property
    def restriction_indexes(self) -> list[tuple[int, int]]:
        """ The indexes of the restriction sequence of the sentence in natural speech"""
        leads_indexes = [(self.natural_index(each_restrict[0]),
                          self.natural_index(each_restrict[1]))
                         for each_restrict in self.restriction_sequence]
        return leads_indexes

    @property
    def prime_syntactic_leads(self) -> list[str]:
        """ Syntactic words which does not follow any other syntactic word"""
        prime_syntactic_leads = [each_word for each_word in self.filling_order
                                 if self[each_word].led_by == "NONE"]
        return prime_syntactic_leads

    @staticmethod
    def normalize_mnemonic(mnemonic: Union[str, list[str]]) -> list[str]:
        """
            Normalize a mnemonic variable to a list of strings

        Parameters
        ----------
        mnemonic : Union[str, list[str]]
            The mnemonic to be normalized

        Returns
        -------
        list[str]
            Return the list of words form the mnemonic
        """
        if isinstance(mnemonic, str):
            mnemonic = mnemonic.split(" ")
        return mnemonic

    def fill_index(self, syntactic_word: str):
        """
            Give the sentence index in the filling order of a given syntactic word

        Parameters
        ----------
        syntactic_word : str
            The word given to find the index in the filling order

        Returns
        -------
        int
            The index of the word given in the filling order
        """
        fill_index = self.filling_order.index(syntactic_word)
        return fill_index

    def restriction_pairs(self, sentence: list[str]) -> list[tuple[str, str]]:
        """
            Find the pairs of restriction from a given sentence

        Parameters
        ----------
        sentence : list[str]
            The list of words from a sentence of the mnemonic

        Returns
        -------
        list[tuple[str, str]]
            The list of restriction relation of the words from the given sentence
            ordered as a tuple of leading word and led word respectively
        """
        restriction_pairs = [(sentence[each_pair[0]],
                              sentence[each_pair[1]])
                             for each_pair in self.restriction_indexes]
        return restriction_pairs

    def get_relation_indexes(self, relation: tuple) -> tuple[int, int]:
        """
            Give the indexes from a given tuple of relation syntactic and mnemonic words
            If any word given only leads and not led, find the indexes in the total_words list

        Parameters
        ----------
        relation : tuple
            The relation given to find the index from the lists
            It can be whether a tuple of syntactic leads and the mnemonic leads
             or a tuple of tuples of syntactic leads and led and mnemonic leads and led
             e.g. ("VERB", word_verb) or (("VERB", "SUBJECT"), (word_verb, word_subject))

        Returns
        -------
        tuple[int, int]
            The tuple with the indexes found in the restriction relation
        """
        syntactic_relation, mnemonic_relation = relation
        if isinstance(syntactic_relation, str) and isinstance(mnemonic_relation, str):
            synt_leads = syntactic_relation
            mnemo_leads = mnemonic_relation
            words_list = self[synt_leads].total_words
            mnemo_index = self.natural_index(syntactic_relation)
            word_index = words_list.index(mnemo_leads)
        else:
            syntactic_relation, mnemonic_relation = relation
            synt_leads, synt_led = syntactic_relation
            mnemo_leads, mnemo_led = mnemonic_relation
            mnemo_index = self.natural_index(synt_led)
            restriction_dict = self[synt_leads][synt_led].mapping
            words_list = restriction_dict[mnemo_leads]
            word_index = words_list.index(mnemo_led)
        return mnemo_index, word_index

    def get_natural_indexes(self, sentence: Union[str, list]) -> list[int]:
        """
            Return the indexes of a sentence from the lists ordered as natural speech of this theme
            The sentence can be given as a list or a string and must be complete
             otherwise raises ValueError exception

        Parameters
        ----------
        sentence: Union[str, list]
            The words to be searched, must have complete sentences

        Returns
        -------
        list[int]
            The list of indexes of the words in this theme lists and ordered as the mnemonic given
        """
        sentence = self.normalize_mnemonic(sentence)
        if len(sentence) != self.words_per_phrase:
            error_message = "The number of words in sentence must be %d, but it is %d"
            raise ValueError(error_message % (len(sentence), self.words_per_phrase))

        word_indexes = [0]*len(sentence)
        restriction_sequence = self.restriction_sequence
        prime_syntactic_leads = self.prime_syntactic_leads
        word_restriction_pairs = self.restriction_pairs(sentence)
        restriction_relation = zip(restriction_sequence, word_restriction_pairs)
        for each_syntactic_leads in prime_syntactic_leads:
            each_relation = (each_syntactic_leads, sentence[self.natural_index(each_syntactic_leads)])
            mnemo_index, word_index = self.get_relation_indexes(each_relation)
            word_indexes[mnemo_index] = word_index
        for each_relation in restriction_relation:
            mnemo_index, word_index = self.get_relation_indexes(each_relation)
            word_indexes[mnemo_index] = word_index
        return word_indexes

    def get_filling_indexes(self, sentence: Union[str, list]) -> list[int]:
        """
            Return the indexes of a sentence from the lists ordered as the filling order of this theme
            The sentence can be given as a list or a string and must be a complete sentence
             otherwise raises ValueError exception

        Parameters
        ----------
        sentence : Union[str, list]
            The words to be searched, must be a complete sentence

        Returns
        -------
        list[int]
            The list of indexes of the words in this theme lists and ordered as the filling order
        """
        sentence = self.normalize_mnemonic(sentence)
        if len(sentence) % self.words_per_phrase != 0:
            error_message = "The number of words in sentence must be %d, but it is %d"
            raise ValueError(error_message % (len(sentence), self.words_per_phrase))

        word_natural_indexes = self.get_natural_indexes(sentence)
        word_fill_indexes = [word_natural_indexes[each_index]
                             for each_index in self.natural_map]
        return word_fill_indexes

    def get_phrase_amount(self, mnemonic: Union[str, list[str]]) -> int:
        """
            Get how many phrases are in the given mnemonic

        Parameters
        ----------
        mnemonic : Union[str, list[str]]
            The mnemonic to get the amount of phrases, it can be a string or a list of words

        Returns
        -------
        int
            Return the amount of phrases of the given mnemonic
        """
        mnemonic = self.normalize_mnemonic(mnemonic)
        mnemonic_size = len(mnemonic)
        phrase_size = self.words_per_phrase
        phrase_amount = mnemonic_size // phrase_size
        return phrase_amount

    def get_sentences(self, mnemonic: Union[str, list[str]]) -> list[list[str]]:
        """
            Split to list the sentences from a given mnemonic

        Parameters
        ----------
        mnemonic : Union[str, list[str]]
            The mnemonic to get the sentences from, it can be a str or a list of words

        Returns
        -------
        list[list[str]]
            Return a list of sentences with the lists of words from the mnemonic
        """
        mnemonic = self.normalize_mnemonic(mnemonic)
        phrase_size = self.words_per_phrase
        phrase_amount = self.get_phrase_amount(mnemonic)
        sentences = [mnemonic[phrase_size*each_phrase:phrase_size*(each_phrase+1)]
                     for each_phrase in range(phrase_amount)]
        return sentences

    def get_phrase_indexes(self, mnemonic: Union[str, list[str]]) -> list[int]:
        """
            Get the indexes of a given mnemonic from each sentence in it
            The mnemonic can be given as a list or a string and must have complete sentences
             otherwise raises ValueError exception

        Parameters
        ----------
        mnemonic : Union[str, list[str]]
            The words to be searched, must have complete sentences

        Returns
        -------
        list[int]
            The list of indexes of the words in this theme lists and ordered as the filling order
        """
        mnemonic = self.normalize_mnemonic(mnemonic)
        sentences = self.get_sentences(mnemonic)
        indexes = [each_fill_index for each_phrase in sentences
                   for each_fill_index in self.get_filling_indexes(each_phrase)]
        return indexes

    def get_lead_mapping(self, syntactic_key):
        lead_mapping = self[self[syntactic_key].led_by][syntactic_key].mapping
        return lead_mapping

    def get_led_by_index(self, syntactic_key: str):
        """
            Get the natural index of the leading word

        Parameters
        ----------
        syntactic_key : str
            The leading word to get the natural index from
        Returns
        -------
        int
            The natural index of the leading word
        """
        led_by_index = self.natural_index(self[syntactic_key].led_by)
        return led_by_index

    def get_lead_list(self, syntactic_key: str, sentence: list) -> list[str]:
        """
            Get the list of words led by the given syntactic word

        Parameters
        ----------
        syntactic_key : str
            The syntactic word which leads the list
        sentence : list
            The sentence to solve the leading when the desired list depends on the leading words
        Returns
        -------
        list[str]
            Return the list led by a syntactic word
        """
        if syntactic_key in self.prime_syntactic_leads:
            lead_list = self[syntactic_key].total_words
        else:
            mapping = self.get_lead_mapping(syntactic_key)
            leading_word = sentence[self.get_led_by_index(syntactic_key)]
            lead_list = mapping[leading_word]
        return lead_list

    def assemble_sentence(self, data_bits: str) -> list[str]:
        """
            Build sentence using bits given following the dictionary filling order

        Parameters
        ----------
        data_bits : str
            The information as bits from the entropy and checksum
            Each step from it represents an index to the list of led words

        Returns
        -------
        list[str]
            The resulting words ordered of sentence in natural language
        """
        bit_index = 0
        current_sentence = [""] * len(self.filling_order)
        for syntactic_key in self.filling_order:

            bit_length = self[syntactic_key].bit_length
            # Integer from substring of zeroes and ones representing index of current word within its list
            word_index = int(data_bits[bit_index: bit_index + bit_length], 2)
            bit_index += bit_length

            list_of_words = self.get_lead_list(syntactic_key, current_sentence)
            syntactic_order = self.natural_index(syntactic_key)
            current_sentence[syntactic_order] = list_of_words[word_index]
        return current_sentence

    def get_sentences_from_bits(self, data_bits: str) -> list[str]:
        """
            Get the mnemonic sentences in the natural speech order from given string of bits

        Parameters
        ----------
        data_bits : str
            The bits of the entropy and checksum to get the sentences from
        Returns
        -------
        list[str]
            Return a list of words forming the sentences of the mnemonic
        """
        phrases_amount = len(data_bits) // self.bits_per_phrase
        sentences = []
        for phrase_index in range(phrases_amount):
            sentence_index = self.bits_per_phrase * phrase_index
            data_segment = data_bits[sentence_index: sentence_index + self.bits_per_phrase]
            sentences += self.assemble_sentence(data_segment)
        return sentences


# Refactored code segments from <https://github.com/keis/base58>
def b58encode(v: bytes) -> str:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    p, acc = 1, 0
    for c in reversed(v):
        acc += p * c
        p = p << 8

    string = ""
    while acc:
        acc, idx = divmod(acc, 58)
        string = alphabet[idx: idx + 1] + string
    return string


class Mnemonic(object):
    DEFAULT_THEME = "BIP39"

    @property
    def is_bip39_theme(self) -> bool:
        """ Evaluates whether the theme chosen is from BIP39 or not"""
        is_bip39 = self.base_theme.startswith(self.DEFAULT_THEME)
        return is_bip39

    def __init__(self, theme: str):
        self.base_theme = theme
        theme_file = Path(__file__).parent.absolute() / Path("themes") / Path("%s.json" % theme)
        if Path.exists(theme_file) and Path.is_file(theme_file):
            with open(theme_file) as json_file:
                self.words_dictionary = ThemeDict(json.load(json_file))
        else:
            raise FileNotFoundError("Theme file not found")
        self.wordlist = self.words_dictionary.wordlist
        # Japanese must be joined by ideographic space
        self.delimiter = "\u3000" if theme == "BIP39_japanese" else " "

    @classmethod
    def find_themes(cls) -> list[str]:
        """
            Look into the themes folder and list .json files as themes found

        Returns
        -------
        list[str]
            The list the name of the themes found in the folder
        """
        themes_path = Path("themes")
        theme_files = [str(each_file).split(".")[0]
                       for each_file in os.listdir(Path(__file__).parent.absolute() / themes_path)
                       if str(each_file).endswith(".json")]
        return theme_files

    @staticmethod
    def normalize_string(txt: Union[str, bytes]) -> str:
        """
            Normalize any given string to the normal from NFKD of Unicode

        Parameters
        ----------
        txt : Union[str, bytes]
            The string to be normalized

        Returns
        -------
        str
            Normalized string NFKD of Unicode
        """
        if isinstance(txt, bytes):
            utxt = txt.decode("utf8")
        elif isinstance(txt, str):
            utxt = txt
        else:
            raise TypeError("String value expected")

        return unicodedata.normalize("NFKD", utxt)

    @classmethod
    def detect_theme(cls, code: Union[str, list[str]]) -> str:
        """
            Find which theme of a given mnemonic,
            Raise error when multiple themes are found, can be caused when there is many shared words between themes

        Parameters
        ----------
        code : Union[str, list[str]]
            The list of mnemonic words

        Returns
        -------
        Union[str, list[str]]
            Unambiguous theme found
        """
        if isinstance(code, list):
            code = " ".join(code)
        code = cls.normalize_string(code)
        possible_themes = set(cls(each_theme) for each_theme in cls.find_themes())
        for word in code.split():
            possible_themes = set(theme for theme in possible_themes if word in theme.wordlist)
            if not possible_themes:
                raise ThemeNotFound(f"Theme unrecognized for {word!r}")
        if len(possible_themes) == 1:
            return possible_themes.pop().base_theme
        else:
            raise ThemeAmbiguous(
                f"Theme ambiguous between {', '.join( theme.base_theme for theme in possible_themes)}"
            )

    def generate(self, strength: int = 128) -> str:
        """
            Create a new mnemonic using a randomly generated entropy number
            For BIP39 as defined, the entropy must be a multiple of 32 bits,
             and its size must be between 128 and 256 bits,
             but it can generate from 32 to 256 bits for any theme

        Parameters
        ----------
        strength : int
            The number os bits randomly generated as entropy
            If not provided, the default entropy length will be set to 128 bits

        Returns
        -------
        str
            Words that encodes the generated entropy
        """
        if strength % 32 != 0 and strength > 256:
            raise ValueError(
                "Strength should be below 256 and a multiple of 32, but it is %d."
                % strength
            )
        return self.to_mnemonic(os.urandom(strength // 8))

    def format_mnemonic(self, mnemonic: Union[str, list[str]]) -> str:
        """
            Format the first line with the password using the first unique letters of each word
             followed by each phrase in new line

        Parameters
        ----------
        mnemonic: Union[str, list[str]]
            The mnemonic to be format

        Returns
        -------
        str
            Return mnemonic string with clearer format
        """
        mnemonic = self.words_dictionary.normalize_mnemonic(mnemonic)
        n = 4 if self.is_bip39_theme else 2
        # Concatenate the first n letters of each word in a single string
        # If the word in BIP39 has 3 letters finish with "-"
        password = ["".join([w[:n] if len(w) >= n else w+"-" for w in mnemonic]) + "\n"]
        phrase_size = self.words_dictionary.words_per_phrase
        password += [" ".join(mnemonic[phrase_size * phrase_index:phrase_size * (phrase_index + 1)]) + "\n"
                     for phrase_index in range(len(mnemonic) // phrase_size)]
        password = "".join(password)[:-1]
        return password

    # Adapted from <http://tinyurl.com/oxmn476>
    def to_entropy(self, words: Union[str, list[str]]) -> bytearray:
        """
            Extract an entropy and checksum values from mnemonic in Formosa standard

        Parameters
        ----------
        words : list or str
            This is the mnemonic that is desired to extract entropy from

        Returns
        -------
        bytearray
            Returns a bytearray with the entropy and checksum values extracted from a mnemonic in a Formosa standard
        """
        if not isinstance(words, list):
            words = words.split(" ")
        words_size = len(words)
        words_dict = self.words_dictionary
        phrase_amount = words_dict.get_phrase_amount(words)
        phrase_size = words_dict.words_per_phrase
        bits_per_checksum_bit = 33
        if words_size % phrase_size != 0:
            error_message = "The number of words must be a multiple of %d, but it is %d"
            raise ValueError(error_message % (phrase_size, words_size))

        # Look up all the words in the list and construct the
        # concatenation of the original entropy and the checksum.

        # Determining strength of the password
        number_phrases = words_size // words_dict.words_per_phrase
        concat_len_bits = round(number_phrases*words_dict.bits_per_phrase)
        checksum_length_bits = round(concat_len_bits//bits_per_checksum_bit)
        entropy_length_bits = concat_len_bits-checksum_length_bits

        idx = map(lambda x, y: bin(x)[2:].zfill(y),
                  words_dict.get_phrase_indexes(words),
                  words_dict.bits_fill_sequence * phrase_amount)
        concat_bits = [bit == "1" for bit in "".join(idx)]

        # Extract original entropy as bytes.
        entropy = bytearray(entropy_length_bits // 8)

        # For every entropy byte
        for entropy_idx in range(len(entropy)):
            # For every entropy bit
            for bit_idx in range(8):
                # Run time performance is sacrificed to avoid side-channel attack
                bit_int = 1 if concat_bits[(entropy_idx * 8) + bit_idx] else 0
                entropy[entropy_idx] |= bit_int << (8 - 1 - bit_idx)
        hash_bytes = hashlib.sha256(entropy).digest()
        hash_bits = list(
            itertools.chain.from_iterable(
                [checksum_byte & (1 << (8 - 1 - bit_idx)) != 0
                 for bit_idx in range(8)]
                for checksum_byte in hash_bytes))

        # Test checksum
        valid = True
        for bit_idx in range(checksum_length_bits):
            valid &= concat_bits[entropy_length_bits + bit_idx] == hash_bits[bit_idx]
        if not valid:
            raise ValueError("Failed checksum.")

        return entropy

    def to_mnemonic(self, data: bytes) -> str:
        """
            Create a mnemonic in Formosa standard from an entropy value

        Parameters
        ----------
        data : bytes
            This is the entropy that is desired to build mnemonic from

        Returns
        -------
        str
            Return the built mnemonic in Formosa standard
        """
        least_multiple = 4
        if len(data) % least_multiple != 0:
            error_message = "Number of bytes should be multiple of %s, but it is %s."
            raise ValueError(error_message % (least_multiple, len(data)))

        hash_digest = hashlib.sha256(data).hexdigest()
        entropy_bits = bin(int.from_bytes(data, byteorder="big"))[2:].zfill(len(data) * 8)
        checksum_bits = bin(int(hash_digest, 16))[2:].zfill(256)[: len(data) * 8 // 32]
        data_bits = entropy_bits + checksum_bits

        sentences = self.words_dictionary.get_sentences_from_bits(data_bits)
        mnemonic = self.delimiter.join(sentences)
        return mnemonic

    @staticmethod
    def convert_theme(mnemonic: Union[str, list[str]],
                      new_theme: str,
                      current_theme: str = None) -> str:
        """
            Convert a mnemonic in a theme to another theme, preserving the original entropy
            The object base theme WILL NOT change to the new theme

        Parameters
        ----------
        mnemonic : [list[str], str]
            The mnemonic to be converted to another theme
        new_theme : str
            The new theme desired to the mnemonic
        current_theme : str
            The current theme of the mnemonic, it is optional but required if it cannot detect the theme

        Returns
        -------
            It returns a new mnemonic with the desired theme preserving the original entropy
        """
        if new_theme not in Mnemonic.find_themes():
            error_message = "Theme %s not found"
            raise FileNotFoundError(error_message % new_theme)
        if isinstance(mnemonic, str):
            mnemonic = mnemonic.split(" ")
        if current_theme is None:
            current_theme = Mnemonic.detect_theme(mnemonic)
            if isinstance(current_theme, list):
                error_message = "Theme detected is ambiguous, is necessary to provide the mnemonic theme"
                raise ThemeAmbiguous(error_message)
        entropy = Mnemonic(current_theme).to_entropy(mnemonic)
        new_mnemonic = Mnemonic(new_theme).to_mnemonic(entropy)
        return new_mnemonic

    def check(self, mnemonic: Union[str, list[str]]) -> bool:
        if isinstance(mnemonic, list):
            mnemonic = " ".join(mnemonic)
        mnemonic_list = self.normalize_string(mnemonic).split(" ")
        # Test the mnemonic length for BIP39 or other theme in each case
        if self.is_bip39_theme and len(mnemonic_list) not in [i for i in range(3, 25, 3)] or \
                not self.is_bip39_theme and len(mnemonic_list) not in [i for i in range(6, 49, 6)]:
            return False
        words_dict = self.words_dictionary
        phrase_amount = words_dict.get_phrase_amount(mnemonic_list)
        try:
            # Get the bits from the filling indexes with the size of word in sequence for phrases
            idx = map(lambda x, y: bin(x)[2:].zfill(y),
                      words_dict.get_phrase_indexes(mnemonic_list),
                      words_dict.bits_fill_sequence * phrase_amount)
            b = "".join(idx)
        except ValueError:
            return False
        l = len(b)  # noqa: E741
        d = b[: l // 33 * 32]
        h = b[-l // 33:]
        nd = int(d, 2).to_bytes(l // 33 * 4, byteorder="big")
        nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[: l // 33]
        return h == nh

    def expand_word(self, prefix: str) -> str:
        if prefix in self.wordlist:
            return prefix
        else:
            matches = [word for word in self.wordlist if word.startswith(prefix)]
            if len(matches) == 1:  # matched exactly one word in the wordlist
                return matches[0]
            else:
                # exact match not found.
                # this is not a validation routine, just return the input
                return prefix

    def expand(self, mnemonic: Union[str, list[str]]) -> str:
        if isinstance(mnemonic, list):
            mnemonic = " ".join(mnemonic)
        mnemonic = self.normalize_string(mnemonic).split(" ")
        if self.is_bip39_theme:
            return " ".join(map(self.expand_word, mnemonic))
        words_dict = self.words_dictionary
        phrase_size = words_dict.words_per_phrase
        sentences = words_dict.get_sentences(mnemonic)
        leading_sequence = words_dict.restriction_sequence
        expanded_mnemonic = []
        for each_phrase in sentences:
            expanded_phrase = [""]*phrase_size
            pairs = words_dict.restriction_pairs(each_phrase)

            for each_pair, each_sequence in zip(pairs, leading_sequence):
                syntactic_leads, syntactic_led = each_sequence
                mnemonic_leads, mnemonic_led = each_pair
                if syntactic_leads in words_dict.prime_syntactic_leads:
                    self.wordlist = words_dict[syntactic_leads].total_words
                    word_index = words_dict.natural_index(syntactic_leads)
                    expanded_phrase[word_index] = self.expand_word(mnemonic_leads)
                led_by_index = words_dict.get_led_by_index(syntactic_led)
                led_by_mapping = words_dict.get_led_by_mapping(syntactic_led)
                word_index = words_dict.natural_index(syntactic_led)
                if expanded_phrase[led_by_index] in led_by_mapping.keys():
                    self.wordlist = led_by_mapping[expanded_phrase[led_by_index]]
                    expanded_phrase[word_index] = self.expand_word(mnemonic_led)
                else:
                    expanded_phrase[word_index] = mnemonic_led

            expanded_mnemonic += expanded_phrase
        expanded_mnemonic = " ".join(expanded_mnemonic)
        self.wordlist = words_dict.wordlist
        return expanded_mnemonic

    def expand_password(self, password: str) -> str:
        """
            Try to recover the mnemonic words from the password which are the first letters of each word

        Parameters
        ----------
        password : str
            The password containing the first letters of each word from the mnemonic

        Returns
        -------
        str
            Return the complete mnemonic recovered from the password
            When the word is not found just return the input
            Note the whole phrase can be missed depending on the position of the missed word
        """
        n = 4 if self.is_bip39_theme else 2
        if len(password) % n != 0:
            return password
        password = " ".join([password[i:i+n-1]
                             if password[i + n - 1] == "-" and self.is_bip39_theme else password[i:i+n]
                             for i in range(0, len(password), n)])
        return self.expand(password)

    @classmethod
    def to_seed(cls, mnemonic: str, passphrase: str = "") -> bytes:

        try:
            theme = cls.detect_theme(mnemonic)
            if not cls.is_bip39_theme:
                mnemonic = cls.convert_theme(mnemonic, cls.DEFAULT_THEME, theme)
        except ThemeNotFound:
            pass

        mnemonic = cls.normalize_string(mnemonic)
        passphrase = cls.normalize_string(passphrase)
        passphrase = "mnemonic" + passphrase
        mnemonic_bytes = mnemonic.encode("utf-8")
        passphrase_bytes = passphrase.encode("utf-8")
        stretched = hashlib.pbkdf2_hmac(
            "sha512", mnemonic_bytes, passphrase_bytes, PBKDF2_ROUNDS
        )
        return stretched[:64]

    @staticmethod
    def to_hd_master_key(seed: bytes, testnet: bool = False) -> str:
        if len(seed) != 64:
            raise ValueError("Provided seed should have length of 64")

        # Compute HMAC-SHA512 of seed
        seed = hmac.new(b"Bitcoin seed", seed, digestmod=hashlib.sha512).digest()

        # Serialization format can be found at:
        # https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#Serialization_format
        xprv = b"\x04\x88\xad\xe4"  # Version for private mainnet
        if testnet:
            xprv = b"\x04\x35\x83\x94"  # Version for private testnet
        xprv += b"\x00" * 9  # Depth, parent fingerprint, and child number
        xprv += seed[32:]  # Chain code
        xprv += b"\x00" + seed[:32]  # Master key

        # Double hash using SHA256
        hashed_xprv = hashlib.sha256(xprv).digest()
        hashed_xprv = hashlib.sha256(hashed_xprv).digest()

        # Append 4 bytes of checksum
        xprv += hashed_xprv[:4]

        # Return base58
        return b58encode(xprv)


def main() -> None:
    if len(sys.argv) == 3:
        theme = sys.argv[1]
        strength = int(sys.argv[2])
        m = Mnemonic(theme)
        print(m.format_mnemonic(m.generate(strength)))
        return
    theme = "BIP39"
    if len(sys.argv) > 1:
        hex_data = sys.argv[1]
    else:
        hex_data = sys.stdin.readline().strip()
    data = bytes.fromhex(hex_data)
    m = Mnemonic(theme)
    print(m.to_mnemonic(data))


if __name__ == "__main__":
    main()

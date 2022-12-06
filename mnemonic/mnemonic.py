#
# Copyright (c) 2013 Pavol Rusnak
# Copyright (c) 2017 mruddy
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
from typing import List, TypeVar, Union
from themes.theme_verify import Verifier, ThemeDict

# This prevents IDE from creating a cache file
sys.dont_write_bytecode = True
_T = TypeVar("_T")
PBKDF2_ROUNDS = 2048


class ConfigurationError(Exception):
    pass


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


def concat_idx_of_words(passphrase: list, concat_bits: list,
                        words_dictionary: dict, phrase_len: int) -> list:
    """
        This function maps each word to each index in the restriction list in form of concatenated bits

    Parameters
    ----------
    passphrase : list
        This is the list of words used in Formosa standard
    concat_bits :list
        This is an empty list to be returned as concatenated bits
    words_dictionary : dict
        This is the base dictionary from which the word lists are consulted
    phrase_len : int
        This is the size of phrase used in the Formosa standard

    Returns
    -------
    list
        Returns the concatenated bits mapped from the passphrase
    """
    bit_idx = 0
    restricting_word = ""

    for sentence_idx in range(len(passphrase) // phrase_len):

        current_sentence = passphrase[phrase_len * sentence_idx: phrase_len * (sentence_idx + 1)]

        for syntactic_key in words_dictionary["FILLING_ORDER"]:
            restricted_by = words_dictionary[syntactic_key]["RESTRICTED_BY"]
            natural_word_position = words_dictionary["NATURAL_ORDER"].index(syntactic_key)
            len_word = words_dictionary[syntactic_key]["BIT_LENGTH"]
            current_word = current_sentence[natural_word_position]
            if restricted_by != "NONE":
                restricting_idx = words_dictionary["NATURAL_ORDER"].index(restricted_by)
                restricting_word = current_sentence[restricting_idx]

            wdict_idx = (
                words_dictionary[syntactic_key]["TOTAL_LIST"].index(current_word)
                if words_dictionary[syntactic_key]["RESTRICTED_BY"] == "NONE" else
                words_dictionary[restricted_by][syntactic_key]["MAPPING"][restricting_word].index(current_word)
            )
            if wdict_idx == -1:
                raise LookupError("Unable to find \"%s\" in the \"%s\" word list." % (current_word, restricted_by))

            for wbit_idx in range(len_word):
                concat_bits[bit_idx] = (wdict_idx & (1 << (len_word - 1 - wbit_idx))) != 0
                bit_idx += 1
    return concat_bits


class Mnemonic(object):
    def __init__(self, theme: str):
        theme_file = self._get_directory() / Path("themes") / Path("%s.json" % theme)
        with open(theme_file) as json_file:
            words_dictionary = json.load(json_file)

        self.words_dictionary = ThemeDict(words_dictionary)
        verifier = Verifier()
        verifier.set_verify_file(self.words_dictionary)
        verifier.start_verification()

    @staticmethod
    def _get_directory() -> Path:
        """
            This method finds out in which directory the code is running

        Returns
        -------
        path
            Returns the absolute path found of the file
        """
        return Path(__file__).parent.absolute()

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
                       for each_file in os.listdir(cls._get_directory() / themes_path)
                       if str(each_file).endswith(".json")]
        return theme_files

    @staticmethod
    def normalize_string(txt: Union[str, bytes]) -> str:
        """
            Normalize any given string to the normal form NFKD of Unicode

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
    def detect_theme(cls, seed_phrase: Union[str, list[str]]) -> Union[str, list[str]]:
        """
            Try to guess which theme used as seed phrase,
            multiple themes can be found when there is shared words between them
            Not compatible with original 'detect_language' because can return a list instead of a string

        Parameters
        ----------
        seed_phrase : str
            The list of words kept as seed

        Returns
        -------
        Union[str, list[str]]
            Possible themes found
        """
        if isinstance(seed_phrase, list):
            seed_phrase = " ".join(seed_phrase)
        seed_phrase = cls.normalize_string(seed_phrase)
        seed_list = seed_phrase.replace("\n", " ").split(" ")
        themes_found = cls.find_themes()

        # Filter themes by the first word of the mnemonic
        primary_themes = []
        first_word = seed_list[0]
        for each_theme in themes_found:
            formosa_theme = cls(each_theme)
            first_syntactic = formosa_theme.words_dictionary.natural_order[0]
            if first_word in formosa_theme.words_dictionary[first_syntactic].total_words:
                primary_themes.append(each_theme)

        # With themes filtered by the first word check the whole mnemonic with the themes found
        possible_themes = []
        for each_theme in primary_themes:
            formosa_theme = cls(each_theme)
            total_words = set()
            for each_key_word in formosa_theme.words_dictionary.natural_order:
                total_words = total_words.union(formosa_theme.words_dictionary[each_key_word].total_words)
            if set(seed_list).issubset(total_words):
                possible_themes.append(each_theme)

        if possible_themes:
            # When there are shared words between themes the result can be ambiguous
            if len(possible_themes) == 1:
                return possible_themes[0]
            else:
                return possible_themes
        else:
            raise ConfigurationError("Theme not detected")

    def generate(self, strength: int = 128) -> str:
        if strength not in range(128, 257, 32):  # [128, 160, 192, 224, 256]:
            raise ValueError(
                "Strength should be one of the following [128, 160, 192, 224, 256], but it is %d."
                % strength
            )
        return self.to_mnemonic(os.urandom(strength // 8))

    # Adapted from <http://tinyurl.com/oxmn476>
    def to_entropy(self, passphrase: Union[List[str], str]) -> bytearray:
        """
            This method extract an entropy and checksum values from passphrase in Formosa standard

        Parameters
        ----------
        passphrase : list or str
            This is the passphrase that is desired to extract entropy from

        Returns
        -------
        bytearray
            Returns a bytearray with the entropy and checksum values extracted from a passphrase in a Formosa standard
        """
        if not isinstance(passphrase, list):
            passphrase = passphrase.split(" ")
        passphrase_size = len(passphrase)
        phrase_len = self.words_dictionary.words_per_phrase
        bits_per_checksum_bit = 33
        if passphrase_size % phrase_len != 0:
            error_message = "The number of words must be a multiple of %d, but it is %d"
            raise ValueError(error_message % (phrase_len, passphrase_size))

        # Look up all the words in the list and construct the
        # concatenation of the original entropy and the checksum.

        # Determining strength of the password
        avg_bits_per_word = self.words_dictionary.bits_per_phrase/self.words_dictionary.words_per_phrase
        concat_len_bits = round(passphrase_size*avg_bits_per_word)
        checksum_length_bits = round(concat_len_bits//bits_per_checksum_bit)
        entropy_length_bits = concat_len_bits-checksum_length_bits

        concat_bits = [False] * concat_len_bits
        concat_bits = list(concat_idx_of_words(passphrase, concat_bits, self.words_dictionary, phrase_len))

        # Extract original entropy as bytes.
        entropy = bytearray(entropy_length_bits // 8)

        # For every entropy byte
        for entropy_idx in range(len(entropy)):
            # For every entropy bit
            for bit_idx in range(8):
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
            This method creates a passphrase in Formosa standard from an entropy and checksum values

        Parameters
        ----------
        data : bytes
            This is the entropy and checksum that is desired to build passphrase from

        Returns
        -------
        str
            Returns a passphrase in a Formosa standard built from a bytes with the entropy and checksum values
        """
        bits_per_hex = 4
        bytes_per_hex = 2 * bits_per_hex
        bits_per_phrase = self.words_dictionary.bits_per_phrase
        phrase_bits = bytes_per_hex * bits_per_phrase
        if len(data) not in range(bits_per_hex, phrase_bits + 1, bits_per_hex):
            number_phrases = len(data) / bits_per_hex
            error_message = "Number of phrases should be 1 to 24, but it is %s."
            raise ValueError(error_message % "%.1f" % number_phrases)

        hash_digest = hashlib.sha256(data).hexdigest()
        entropy_bits = bin(int.from_bytes(data, byteorder="big"))[2:].zfill(len(data) * 8)
        checksum_bits = bin(int(hash_digest, 16))[2:].zfill(256)[: len(data) * 8 // 32]
        data_bits = entropy_bits + checksum_bits

        phrases_quantity = len(data_bits) // bits_per_phrase
        sentences = []
        for phrase_index in range(phrases_quantity):
            sentence_index = bits_per_phrase * phrase_index
            data_segment = data_bits[sentence_index: sentence_index + bits_per_phrase]
            sentences += self.assemble_sentence(data_segment)
        mnemonic = " ".join(sentences)
        return mnemonic

    def assemble_sentence(self, data_bits: str) -> list[str]:
        """
            Build a pseudo-phrase using bits given and dictate by the dictionary filling order

        Parameters
        ----------
        data_bits : str
            The information as bits from the entropy and checksum
            Each step from it represents an index to the list of restricted words

        Returns
        -------
        list[str]
            It is a list of result words in the order to be used as phrase in natural language
        """
        bit_index = 0
        current_sentence = [""]*len(self.words_dictionary.filling_order)
        for syntactic_key in self.words_dictionary.filling_order:
            current_dictionary = self.words_dictionary[syntactic_key]

            restricted_by = current_dictionary.restricted_by
            if restricted_by != "NONE":
                mapped_dictionary = self.words_dictionary[restricted_by][syntactic_key]
                last_index = self.words_dictionary.natural_order.index(restricted_by)
                last_word = current_sentence[last_index]
                list_of_words = mapped_dictionary.mapping[last_word]
            else:
                list_of_words = current_dictionary.total_words

            syntactic_order = self.words_dictionary.natural_order.index(syntactic_key)
            bit_length = current_dictionary.bit_length
            # Integer from substring of zeroes and ones representing index of current word within its list
            word_dict_index = int(data_bits[bit_index: bit_index + bit_length], 2)
            bit_index += bit_length
            current_sentence[syntactic_order] = list_of_words[word_dict_index]
        return current_sentence

    def convert_theme(self, passphrase: Union[list[str], str], new_theme: str, current_theme: str = None) -> str:
        """
            Translate a mnemonic in a theme to another theme, preserving the original entropy

        Parameters
        ----------
        passphrase : [list[str], str]
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
        if isinstance(passphrase, str):
            passphrase = passphrase.split(" ")
        if current_theme is None:
            current_theme = Mnemonic.detect_theme(passphrase)
            if isinstance(current_theme, list):
                error_message = "Theme detected is ambiguous, is necessary to provide the mnemonic theme"
                raise Exception(error_message)
        entropy = Mnemonic(current_theme).to_entropy(passphrase)
        new_mnemonic = Mnemonic(new_theme)
        self.words_dictionary = new_mnemonic.words_dictionary
        new_passphrase = new_mnemonic.to_mnemonic(entropy)
        return new_passphrase

#    ------------------------hardcoded------------------------
    def check_item(self, mnemonic: str) -> bool:
        mnemonic_list = self.normalize_string(mnemonic).split(" ")
        # list of valid mnemonic lengths
        if len(mnemonic_list) not in range(12, 25, 3):
            return False
        try:
            idx = map(
                lambda x: bin(self.wordlist.index(x))[2:].zfill(11), mnemonic_list
            )
            b = "".join(idx)
        except ValueError:
            return False
        l = len(b)  # noqa: E741
        d = b[: l // 33 * 32]
        h = b[-l // 33:]
        nd = int(d, 2).to_bytes(l // 33 * 4, byteorder="big")
        nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[: l // 33]
        return h == nh
#       ------------------------hardcoded------------------------

    def expand_word(self, prefix: str) -> str:
        for i in range(4):
            self.wlist = str(self.wordlist[i][:])
            if prefix in self.wlist:
                return prefix
            else:
                matches = [word for word in self.wlist if word.startswith(prefix)]
                if len(matches) == 1:  # matched exactly one word in the wordlist
                    return matches[0]
                else:
                    # exact match not found.
                    # this is not a validation routine, just return the input
                    return prefix
#       ------------------------hardcoded------------------------

    def expand(self, mnemonic: str) -> str:
        return " ".join(map(self.expand_word, mnemonic.split(" ")))
#   ------------------------hardcoded------------------------

    @classmethod
    def to_seed(cls, mnemonic: str, passphrase: str = "") -> bytes:
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
    if len(sys.argv) > 1:
        hex_data = sys.argv[1]
    else:
        hex_data = sys.stdin.readline().strip()
    data = bytes.fromhex(hex_data)
    m_bip = Mnemonic("BIP39")
    print(m_bip.to_mnemonic(data))


if __name__ == "__main__":
    main()

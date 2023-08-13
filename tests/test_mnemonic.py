#!/usr/bin/env python3
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

import json
import random
import unittest
from typing import List

from mnemonic import Mnemonic


class MnemonicTest(unittest.TestCase):
    def _check_list(self, language: str, vectors: List[str]) -> None:
        mnemo = Mnemonic(language)
        for v in vectors:
            code = mnemo.to_mnemonic(bytes.fromhex(v[0]))
            seed = Mnemonic.to_seed(code, passphrase="TREZOR")
            xprv = Mnemonic.to_hd_master_key(seed)
            self.assertIs(mnemo.check(v[1]), True, language)
            self.assertEqual(v[1], code, language)
            self.assertEqual(v[2], seed.hex(), language)
            self.assertEqual(v[3], xprv, language)

    def test_vectors(self) -> None:
        with open("vectors.json", "r") as f:
            vectors = json.load(f)
        for lang in vectors.keys():
            self._check_list(lang, vectors[lang])

    def test_failed_checksum(self) -> None:
        code = (
            "bless cloud wheel regular tiny venue bird web grief security dignity zoo"
        )
        mnemo = Mnemonic("english")
        self.assertFalse(mnemo.check(code))

    def test_detection(self) -> None:
        self.assertEqual("english", Mnemonic.detect_language("security"))

        with self.assertRaises(Exception):
            Mnemonic.detect_language(
                "jaguar xxxxxxx"
            )  # Unrecognized in any known language

        with self.assertRaises(Exception):
            Mnemonic.detect_language(
                "jaguar jaguar"
            )  # Ambiguous after examining all words

        self.assertEqual("english", Mnemonic.detect_language("jaguar security"))
        self.assertEqual("french", Mnemonic.detect_language("jaguar aboyer"))

    def test_utf8_nfkd(self) -> None:
        # The same sentence in various UTF-8 forms
        words_nfkd = "Pr\u030ci\u0301s\u030cerne\u030c z\u030clut\u030couc\u030cky\u0301 ku\u030an\u030c u\u0301pe\u030cl d\u030ca\u0301belske\u0301 o\u0301dy za\u0301ker\u030cny\u0301 uc\u030cen\u030c be\u030cz\u030ci\u0301 pode\u0301l zo\u0301ny u\u0301lu\u030a"
        words_nfc = "P\u0159\xed\u0161ern\u011b \u017elu\u0165ou\u010dk\xfd k\u016f\u0148 \xfap\u011bl \u010f\xe1belsk\xe9 \xf3dy z\xe1ke\u0159n\xfd u\u010de\u0148 b\u011b\u017e\xed pod\xe9l z\xf3ny \xfal\u016f"
        words_nfkc = "P\u0159\xed\u0161ern\u011b \u017elu\u0165ou\u010dk\xfd k\u016f\u0148 \xfap\u011bl \u010f\xe1belsk\xe9 \xf3dy z\xe1ke\u0159n\xfd u\u010de\u0148 b\u011b\u017e\xed pod\xe9l z\xf3ny \xfal\u016f"
        words_nfd = "Pr\u030ci\u0301s\u030cerne\u030c z\u030clut\u030couc\u030cky\u0301 ku\u030an\u030c u\u0301pe\u030cl d\u030ca\u0301belske\u0301 o\u0301dy za\u0301ker\u030cny\u0301 uc\u030cen\u030c be\u030cz\u030ci\u0301 pode\u0301l zo\u0301ny u\u0301lu\u030a"

        passphrase_nfkd = (
            "Neuve\u030cr\u030citelne\u030c bezpec\u030cne\u0301 hesli\u0301c\u030cko"
        )
        passphrase_nfc = "Neuv\u011b\u0159iteln\u011b bezpe\u010dn\xe9 hesl\xed\u010dko"
        passphrase_nfkc = (
            "Neuv\u011b\u0159iteln\u011b bezpe\u010dn\xe9 hesl\xed\u010dko"
        )
        passphrase_nfd = (
            "Neuve\u030cr\u030citelne\u030c bezpec\u030cne\u0301 hesli\u0301c\u030cko"
        )

        seed_nfkd = Mnemonic.to_seed(words_nfkd, passphrase_nfkd)
        seed_nfc = Mnemonic.to_seed(words_nfc, passphrase_nfc)
        seed_nfkc = Mnemonic.to_seed(words_nfkc, passphrase_nfkc)
        seed_nfd = Mnemonic.to_seed(words_nfd, passphrase_nfd)

        self.assertEqual(seed_nfkd, seed_nfc)
        self.assertEqual(seed_nfkd, seed_nfkc)
        self.assertEqual(seed_nfkd, seed_nfd)

    def test_to_entropy(self) -> None:
        data = [bytes(random.getrandbits(8) for _ in range(32)) for _ in range(1024)]
        data.append(b"Lorem ipsum dolor sit amet amet.")
        m = Mnemonic("english")
        for d in data:
            self.assertEqual(m.to_entropy(m.to_mnemonic(d).split()), d)

    def test_expand_word(self) -> None:
        m = Mnemonic("english")
        self.assertEqual("", m.expand_word(""))
        self.assertEqual(" ", m.expand_word(" "))
        self.assertEqual("access", m.expand_word("access"))  # word in list
        self.assertEqual(
            "access", m.expand_word("acce")
        )  # unique prefix expanded to word in list
        self.assertEqual("acb", m.expand_word("acb"))  # not found at all
        self.assertEqual("acc", m.expand_word("acc"))  # multi-prefix match
        self.assertEqual("act", m.expand_word("act"))  # exact three letter match
        self.assertEqual(
            "action", m.expand_word("acti")
        )  # unique prefix expanded to word in list

    def test_expand(self) -> None:
        m = Mnemonic("english")
        self.assertEqual("access", m.expand("access"))
        self.assertEqual(
            "access access acb acc act action", m.expand("access acce acb acc act acti")
        )


def __main__() -> None:
    unittest.main()


if __name__ == "__main__":
    __main__()

#!/usr/bin/python
#
# Copyright (c) 2013 Pavol Rusnak
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

import unittest
import json
import hashlib

from Crypto.Cipher.AES import AESCipher
from mnemonic.rijndael import Rijndael, AES as RijnAES

from binascii import hexlify, unhexlify
from mnemonic import Mnemonic

class MnemonicTest(unittest.TestCase):
    def _check_list(self, language, vectors):
        mnemo = Mnemonic(language)
        for v in vectors:
            code = mnemo.encode(unhexlify(v[0]))
            data = hexlify(mnemo.decode(code))

            self.assertEqual(v[1], code)
            self.assertEqual(v[0], data)

            print "input    :", v[0], "(%d bits)" % len(v[0] * 4)
            print "mnemonic :", code, "(%d words)" % len(code.split(' '))
            print

    def test_vectors(self):
        vectors = json.load(open('vectors.json', 'r'))
        for lang in vectors.keys():
            self._check_list(lang, vectors[lang])

    def test_failed_checksum(self):
        code = 'bless cloud wheel regular tiny venue bird web grief security dignity language'
        mnemo = Mnemonic('english')

        with self.assertRaises(Exception):
            mnemo.decode(code)

    def test_passphrase(self):
        vector = json.load(open('vectors.json', 'r'))['english'][0]
        mnemo = Mnemonic('english')
        code = mnemo.encode(unhexlify(vector[0]), 'passphrase')
        data = hexlify(mnemo.decode(code, 'passphrase'))

        self.assertEqual(vector[0], data)
        
    def test_detection(self):
        self.assertEqual('english', Mnemonic.detect_language('eat'))

        with self.assertRaises(Exception):
            Mnemonic.detect_language('xxxxxxx')

    def test_collision(self):
        # Check for the same words accross wordlists.
        # This is prohibited because of auto-detection feature of language.

        words = []
        languages = Mnemonic.list_languages()
        for lang in languages:
            mnemo = Mnemonic(lang)
            words += mnemo.wordlist

        words_unique = list(set(words[:]))
        self.assertEquals(len(words), len(words_unique))

    def test_lengths(self):
        # check if wordlists contain words between 3 and 8 characters
        languages = Mnemonic.list_languages()
        for lang in languages:
            mnemo = Mnemonic(lang)
            words = [w for w in mnemo.wordlist if len(w) < 3 or len(w) > 8]
            print "Language '%s'" % lang
            self.assertListEqual(words, [])

    def test_validchars(self):
        # check if wordlists contain valid characters
        languages = Mnemonic.list_languages()
        for lang in languages:
            mnemo = Mnemonic(lang)
            letters = set(sum([list(w) for w in mnemo.wordlist] ,[]))
            print "Language '%s'" % lang
            for l in letters:
                self.assertIn(l, 'abcdefghijklmnopqrstuvwxyz')

    def test_sorted_unique(self):
        # Check for duplicated words in wordlist

        print "------------------------------------"
        print "Test of sorted and unique wordlists:"

        languages = Mnemonic.list_languages()
        for lang in languages:
            mnemo = Mnemonic(lang)
            unique = list(set(mnemo.wordlist))
            unique.sort()

            print "Language '%s'" % lang
            self.assertListEqual(unique, mnemo.wordlist)

    def test_root_len(self):
        print "------------------------------------"
        print "Test of word prefixes:"

        languages = Mnemonic.list_languages()
        problems_found = 0

        for lang in languages:
            mnemo = Mnemonic(lang)
            prefixes = []
            for w in mnemo.wordlist:
                pref = w[:4]
                if pref in prefixes:
                    words = [ w2 for w2 in mnemo.wordlist if w2[:4] == pref ]
                    print "Duplicate prefix", pref, "for words", words
                    problems_found += 1

                prefixes.append(pref)

        self.assertEqual(problems_found, 0)

    def test_rijndael(self):
        block_sizes = ((16, {
                     '\x00': 'a3af8b7d326a2d47bd7576012e07d103',
                     '\xff': 'e720f4474b7dabe382eec0529e2b1128',
                     'hojda': '9c3bb85af2122cc2df449033338beb56',
                     }),
                    (24, {
                     '\x00': '7b8704678f263c316ddd1746d8377a4046a99dd9e5687d59',
                     '\xff': '14dfe4c7a93e14616dce6c793110baee0b8bb404f3bec6c5',
                     'hojda': '0d7009c589869eaa1d7398bffc7660cce32207a520d6cafe',
                     }),
                    (32, {
                     '\x00': '7c0575db9badc9960441c6b8dcbd5ebdfec522ede5309904b7088d0e77c2bcef',
                     '\xff': 'ccf498fd9a57f872a4d274549fab474cbacdbd9d935ca31b06e3025526a704fb',
                     'hojda': 'b1a4d05e3827611c5986ea4c207679a6934f20767434218029c4b3b7a53806a3',
                     })
            )

        key = hashlib.sha256('mnemonic').digest()


        for block_size, patterns in block_sizes:
            for pattern in patterns.keys():
                rijn = Rijndael(key, block_size=block_size)
                data = pattern * block_size

                cipher = hexlify(rijn.encrypt(data[:block_size]))
                self.assertEqual(patterns[pattern], cipher)

    def test_stretching(self):
        '''
            Test is stretching algorithm is symmetric
            and produces desired string length
        '''
        mnemo = Mnemonic('english')

        for x in (16, 24, 32):
            data = '0' * x
            stretched = mnemo.stretch(data, 'passphrase')
            unstretched = mnemo.unstretch(stretched, 'passphrase')

            self.assertEqual(x, len(stretched))
            self.assertEqual(data, unstretched)

    def test_aes_compatibility(self):
        '''
            This tests if our Rijndael implementation is compatible
            with AES, because:

                Rijndael(block_size=16) <==> AES()
        '''
        data = '0' * 16
        key = hashlib.sha256('mnemonic').digest()
        rijn = RijnAES(key)
        aes = AESCipher(key)

        cipher1 = aes.encrypt(data)
        cipher2 = rijn.encrypt(data)

        # Both libraries now decrypt cipher from another lib
        cross_decrypt1 = rijn.decrypt(cipher1)
        cross_decrypt2 = aes.decrypt(cipher1)

        self.assertEqual(cipher1, cipher2)
        self.assertEqual(data, cross_decrypt1)
        self.assertEqual(data, cross_decrypt2)

def __main__():
    unittest.main()
if __name__ == "__main__":
    __main__()

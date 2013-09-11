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

from binascii import hexlify, unhexlify
from random import choice
from mnemonic import Mnemonic

class MnemonicTest(unittest.TestCase):
    '''
    def test_random(self):
        mnemo = Mnemonic('english')

        for i in range(12):
            data = ''.join(chr(choice(range(0,256))) for _ in range(8 * (i % 3 + 2)))
            print 'input    : %s (%d bits)' % (hexlify(data), len(data) * 8)
            code = mnemo.encode(data)
            print 'mnemonic : %s (%d words)' % (code, len(code.split(' ')))
            data = mnemo.decode(code)
            print 'output   : %s (%d bits)' % (hexlify(data), len(data) * 8)
            print
    '''

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

    def test_corner(self):
        data = []
        for l in range(4, 32 + 1, 4):
            for b in ['00', '7f', '80', 'ff']:
                data.append(b * l)
        codes = [
            'abandon abandon abandon',
            'liberty wing ten',
            'line advance burial',
            'zoo zoo zone',
            'abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave saturday',
            'line advance burst abuse always double',
            'zoo zoo zoo zoo zoo young',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used letter',
            'line advance burst abuse always down acid author light',
            'zoo zoo zoo zoo zoo zoo zoo zoo yell',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used liberty wing ten worth',
            'line advance burst abuse always down acid author line advance burst abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo worth',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used liberty wing ten year wave sauce winner',
            'line advance burst abuse always down acid author line advance burst abuse always down abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo winner',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used liberty wing ten year wave sauce worry used liberty way',
            'line advance burst abuse always down acid author line advance burst abuse always down acid author line abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo way',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used liberty wing ten year wave sauce worry used liberty wing ten year useful',
            'line advance burst abuse always down acid author line advance burst abuse always down acid author line advance burst abuse abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo useful',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'liberty wing ten year wave sauce worry used liberty wing ten year wave sauce worry used liberty wing ten year wave sauce worry tennis',
            'line advance burst abuse always down acid author line advance burst abuse always down acid author line advance burst abuse always down acid abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo tennis',
        ]
        vectors = zip(data, codes)
        self._check_list('english', vectors)

    def test_english(self):
        vectors = \
           [('19458fe8dace41e60617c6667874f6be',
            'block coast when remind title version bizarre website half seminar disease learn'),
            ('2d8fc7c27a52995bc165a0dcead7c169f301652f0b5db145',
            'column leisure utter violin city puppy ahead region sword fiscal usual squad core rebel rough hospital rank continue'),
            ('cbeb354834fffb79bc952458705d2205f79c515e4c91043dc16f3dd6139b3219',
            'slam foot famous history youth rubber velvet pig flip lot endless argue knee choice kingdom mutual adverse unlike friday language glance smile sibling ceiling'),
            ('ea88c6efbc4028994b8b4ebc0345a474',
            'tuna elegant rose key action ever company hip rotate body hero trip'),
            ('bb8e02d2c0fe4c18f60e173bc38724902395b63b1b47bf18',
            'rookie include relax local toilet army stuff seed diamond both silent bus deny sure unaware here same shell'),
            ('0b57161fd701c6c6548db5a71df70166965eec2f16a675acad3ed3460cb3e72f',
            'april rhythm math purchase bounce govern fancy report pocket usage scan slow gun jazz round stage jacket guess explain pledge girl forest organ widow'),
            ('666fbb72dada90d6c8f627d77450f366',
            'half leg swing remove post horror carpet settle street pencil dilemma slight'),
            ('29932c2887ff2c72dd8f9cff1b7ee498119f330d1dd81659',
            'city october answer aunt verb depart jealous viable yell swallow ride corn board odd cup rocket bench snack'),
            ('869e2bc8286611bce2159b89c5a8a4029666dc186bbfe8756ac505a4e89f481e',
            'march valley vast fact glad talk maximum recycle member collect chunk age half icon globe junk trial prison rank april exhaust explain bush slice'),
            ('d0263588b1deee8186818319515c6691',
            'soon craft goal grain uphold drama boat correct block mess blouse carpet'),
            ('48754ef698334cf9cc5494ccca6a0294bf30224066576a7c',
            'end pretty runway correct curtain lawsuit cover myth slight fault link citizen version awful accord skate holiday tiny'),
            ('ee9e8ce85eadcdf0f5473d7490816d9b1335f7204e7776597ac99f9e29186364',
            'unveil village derive rumor switch wear stand trap iraqi lunch french data cross wind little sock jeans sky reason dollar thumb mill mistake net'),
            ]

        self._check_list('english', vectors)

    def test_failed_checksum(self):
        code = 'bless cloud wheel regular tiny venue bird web grief security dignity language'
        mnemo = Mnemonic('english')

        with self.assertRaises(Exception):
            mnemo.decode(code)

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
                pref = w[:5]
                if pref in prefixes:
                    words = [ w2 for w2 in mnemo.wordlist if w2[:5] == pref ]
                    print "Duplicate prefix", pref, "for words", words
                    problems_found += 1

                prefixes.append(pref)

        self.assertEqual(problems_found, 0)
def __main__():
    unittest.main()
if __name__ == "__main__":
    __main__()

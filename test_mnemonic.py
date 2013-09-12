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
            'abbey abbey abbey',
            'lodge wing they',
            'lounge advice calcium',
            'zoo zoo zone',
            'abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way scrap',
            'lounge advice call accept amazing duvet',
            'zoo zoo zoo zoo zoo youth',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lobby',
            'lounge advice call accept amazing dynamic acquire average loop',
            'zoo zoo zoo zoo zoo zoo zoo zoo yellow',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lodge wing they worry',
            'lounge advice call accept amazing dynamic acquire average lounge advice call abbey',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo worry',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lodge wing they year way screen winner',
            'lounge advice call accept amazing dynamic acquire average lounge advice call accept amazing dynamic abbey',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo winner',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lodge wing they year way screen world vacant lodge wealth',
            'lounge advice call accept amazing dynamic acquire average lounge advice call accept amazing dynamic acquire average lounge abbey',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wealth',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lodge wing they year way screen world vacant lodge wing they year vaccine',
            'lounge advice call accept amazing dynamic acquire average lounge advice call accept amazing dynamic acquire average lounge advice call accept abbey',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vaccine',
            'abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey',
            'lodge wing they year way screen world vacant lodge wing they year way screen world vacant lodge wing they year way screen world thing',
            'lounge advice call accept amazing dynamic acquire average lounge advice call accept amazing dynamic acquire average lounge advice call accept amazing dynamic acquire abbey',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo thing',
        ]
        vectors = zip(data, codes)
        self._check_list('english', vectors)

    def test_english(self):
        vectors = \
           [('19458fe8dace41e60617c6667874f6be',
            'board comfort when rest tonight viable blast wedding hip setup drain light'),
            ('2d8fc7c27a52995bc165a0dcead7c169f301652f0b5db145',
            'control lip valley visit cliff quick air render tank foster vague steak crane region saddle immense rebuild correct'),
            ('cbeb354834fffb79bc952458705d2205f79c515e4c91043dc16f3dd6139b3219',
            'smoke gallery find hurt zebra salad verse plastic fructose mammal essence arm law clarify large need aerobic upgrade genius lens grief soft since chaos'),
            ('ea88c6efbc4028994b8b4ebc0345a474',
            'twice enhance russian lamp actor fabric copper hurry sad boom human try'),
            ('bb8e02d2c0fe4c18f60e173bc38724902395b63b1b47bf18',
            'runway invest replace mackerel tortoise around suit series document breeze six calm diamond swing unfold huge scheme shop'),
            ('0b57161fd701c6c6548db5a71df70166965eec2f16a675acad3ed3460cb3e72f',
            'arch road mention quintuple bridge hamster fine rhythm popular utility season sock hide kind sadness stock kick hen federal pond great gap oven widow'),
            ('666fbb72dada90d6c8f627d77450f366',
            'hip line talent result prepare image cattle sheriff success piano dose soap'),
            ('29932c2887ff2c72dd8f9cff1b7ee498119f330d1dd81659',
            'cliff olympic apart autumn vessel diary kingdom victory yellow table rocket crash bonus omit dawn rug better solution'),
            ('869e2bc8286611bce2159b89c5a8a4029666dc186bbfe8756ac505a4e89f481e',
            'measure vast verb fiber grid tenant mercy remain migrant consider clean agree hip inmate grow labor truck proof rebuild arch farm federal camera sniff'),
            ('d0263588b1deee8186818319515c6691',
            'speech crucial guilt hard usage earn book crawl board minor bolster cattle'),
            ('48754ef698334cf9cc5494ccca6a0294bf30224066576a7c',
            'essay problem satisfy crawl deal license crop neither soap five love client viable bacon account slight hyperbole toilet'),
            ('ee9e8ce85eadcdf0f5473d7490816d9b1335f7204e7776597ac99f9e29186364',
            'upset virus dignity same talk weather stone trigger junk march gear defense custom wind lucky sound kiss smile reform duck tip mobile moon nominee'),
            ]

        self._check_list('english', vectors)

    def test_failed_checksum(self):
        code = 'bless cloud wheel regular tiny venue bird web grief security dignity language'
        mnemo = Mnemonic('english')

        with self.assertRaises(Exception):
            mnemo.decode(code)

    def test_detection(self):
        self.assertEqual('english', Mnemonic.detect_language('say'))

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
		
        last = None
        for word in words:
		    if last:
			    self.assertNotEqual(last[:4], word[:4])
		    last = word

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

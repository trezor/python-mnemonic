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
        mnemo = Mnemonic()

        for i in range(12):
            data = ''.join(chr(choice(range(0,256))) for _ in range(8 * (i % 3 + 2)))
            print ''%s (%d bits)' % (hexlify(data), len(data) * 8)
            code = mnemo.encode(data)
            print ''%s (%d words)' % (code, len(code.split(' ')))
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

            print "input:   ", v[0], "(%d bits)" % len(v[0]*4)
            print "mnemonic:", code, "(%d words)" % len(code.split(' '))
            print

    def test_corner(self):
        data = []
        for l in range(4, 32 + 1, 4):
            for b in ['00', '7f', '80', 'ff']:
                data.append(b * l)
        codes = [
            'abandon abandon abandon',
            'legal wing taxi',
            'lethal adult bundle',
            'zoo zoo zone',
            'abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salad',
            'lethal adult bunker absurd also dog',
            'zoo zoo zoo zoo zoo young',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge lecture',
            'lethal adult bunker absurd also domain achieve aunt lens',
            'zoo zoo zoo zoo zoo zoo zoo zoo year',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge legal wing taxi worth',
            'lethal adult bunker absurd also domain achieve aunt lethal adult bunker abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo worth',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge legal wing taxi yard water salmon winner',
            'lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd also domain abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo winner',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge legal wing taxi yard water salmon worry urge legal wave',
            'lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd also domain achieve aunt lethal abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wave',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge legal wing taxi yard water salmon worry urge legal wing taxi yard usage',
            'lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo usage',
            'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon',
            'legal wing taxi yard water salmon worry urge legal wing taxi yard water salmon worry urge legal wing taxi yard water salmon worry team',
            'lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd also domain achieve aunt lethal adult bunker absurd also domain achieve abandon',
            'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo team',
        ]
        vectors = zip(data, codes)
        self._check_list('english', vectors)

    def test_english(self):
        vectors = \
           [('19458fe8dace41e60617c6667874f6be',
            'bless cloud wheel regular tiny venue birth web grief security dignity language'),
            ('2d8fc7c27a52995bc165a0dcead7c169f301652f0b5db145',
            'code laugh useless view chunk property agent rebuild swedish fiction used spoon convince rank role hold race company'),
            ('cbeb354834fffb79bc952458705d2205f79c515e4c91043dc16f3dd6139b3219',
            'sketch flavor eyebrow height youth rope various pet fish little embryo arena just chicken jump mourn advance unique fork knock general slice short caught'),
            ('ea88c6efbc4028994b8b4ebc0345a474',
            'try educate robust joke act erosion color hedge rock blow hat tribe'),
            ('bb8e02d2c0fe4c18f60e173bc38724902395b63b1b47bf18',
            'river ignore recycle like tobacco armor straw season despair bosnian sibling burden defy sunset typical harvest sad shadow'),
            ('0b57161fd701c6c6548db5a71df70166965eec2f16a675acad3ed3460cb3e72f',
            'approach response map protect both glass fabric remember place upset satisfy slave gravity irish romance squad involve grain excuse pioneer gauge flight open white'),
            ('666fbb72dada90d6c8f627d77450f366',
            'grief last swamp reject pond history car sentence stone patrol diamond slam'),
            ('29932c2887ff2c72dd8f9cff1b7ee498119f330d1dd81659',
            'chunk oak another audit vendor degree iron very year surprise retreat cook blossom obey crowd riot belt slogan'),
            ('869e2bc8286611bce2159b89c5a8a4029666dc186bbfe8756ac505a4e89f481e',
            'magnet vacuum van exotic gear tactic march ready matrix coat chin after grief huge genuine jet travel prepare race approach evil excuse burial skirt'),
            ('d0263588b1deee8186818319515c6691',
            'soda country ghost glove unusual dose blouse cope bless medal block car'),
            ('48754ef698334cf9cc5494ccca6a0294bf30224066576a7c',
            'embrace poverty royal cope cruise lake cotton movie slam false letter chuckle venue awesome accident sing hen tight'),
            ('ee9e8ce85eadcdf0f5473d7490816d9b1335f7204e7776597ac99f9e29186364',
            'unlikely victory dentist round swear weapon squeeze traffic insist logo force custom create win liberty snack island skate range display thought merchant migrant nasty'),
            ]

        self._check_list('english', vectors)

def __main__():
    unittest.main()
if __name__ == "__main__":
    __main__()
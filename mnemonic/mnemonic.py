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

import binascii
import hashlib
import hmac
import io
import itertools
import os
import sys
import unicodedata
from pbkdf2 import PBKDF2

PBKDF2_ROUNDS = 2048

class ConfigurationError(Exception):
    pass

class Mnemonic(object):
    IDEOGRAPHIC_SPACE = u'\u3000'

    def __init__(self, language):
        self.radix = 2048
        self.language = language.lower()
        self.joiner = Mnemonic.IDEOGRAPHIC_SPACE if self.language == 'japanese' else u' '
        with io.open('{}/{}.txt'.format(self._get_directory(), self.language), mode='rt', encoding='utf-8', newline=u'\n') as lines:
            self.wordlist = [unicodedata.normalize('NFKD', line).strip() for line in lines] # python2: unicode, python3: str
        if len(self.wordlist) != self.radix:
            raise ConfigurationError('Wordlist should contain %d words, but it contains %d words.' % (self.radix, len(self.wordlist)))

    @classmethod
    def _get_directory(cls):
        return os.path.join(os.path.dirname(__file__), 'wordlist')

    @classmethod
    def list_languages(cls):
        return [f.split('.')[0] for f in os.listdir(cls._get_directory()) if f.endswith('.txt')]

    @classmethod
    def normalize_string(cls, txt):
        if isinstance(txt, str if sys.version < '3' else bytes):
            utxt = txt.decode('utf8')
        elif isinstance(txt, unicode if sys.version < '3' else str):
            utxt = txt
        else:
            raise TypeError("String value expected")

        return unicodedata.normalize('NFKD', utxt)

    @classmethod
    def detect_language(cls, code):
        first = Mnemonic.normalize_string(code).split(u' ')[0]
        languages = cls.list_languages()

        found = []

        for lang in languages:
            mnemo = cls(lang)
            if first in mnemo.wordlist:
                found.append(lang)

        if len(found) == 1:
            return found[0]
        else:
            raise ConfigurationError("Language not detected %s" % found)

    def generate(self, strength=128):
        if strength not in [128, 160, 192, 224, 256]:
            raise ValueError('Strength should be one of the following [128, 160, 192, 224, 256], but it is not (%d).' % strength)
        return self.to_mnemonic(os.urandom(strength // 8))

    # Adapted from <http://tinyurl.com/oxmn476>
    def to_entropy(self, words):
        if not isinstance(words, list):
            words = Mnemonic.normalize_string(words).split(u' ')
        if len(words) not in [12, 15, 18, 21, 24]:
            raise ValueError('Number of words must be one of the following: [12, 15, 18, 21, 24], but it is not (%d).' % len(words))
        # Look up all the words in the list and construct the
        # concatenation of the original entropy and the checksum.
        concatLenBits = len(words) * 11
        concatBits = [False] * concatLenBits
        wordindex = 0
        for word in words:
            # Find the word's index in the wordlist. ValueError if not found.
            ndx = self.wordlist.index(word)
            # Set the next 11 bits to the value of the index.
            for ii in range(11):
                concatBits[(wordindex * 11) + ii] = (ndx & (1 << (10 - ii))) != 0
            wordindex += 1
        checksumLengthBits = concatLenBits // 33
        entropyLengthBits = concatLenBits - checksumLengthBits
        # Extract original entropy as bytes.
        entropy = bytearray(entropyLengthBits // 8)
        for ii in range(len(entropy)):
            for jj in range(8):
                if concatBits[(ii * 8) + jj]:
                    entropy[ii] |= 1 << (7 - jj)
        # Take the digest of the entropy.
        hashBytes = hashlib.sha256(entropy).digest()
        if sys.version < '3':
            hashBits = list(itertools.chain.from_iterable(([ord(c) & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes)))
        else:
            hashBits = list(itertools.chain.from_iterable(([c & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes)))
        # Check all the checksum bits.
        for i in range(checksumLengthBits):
            if concatBits[entropyLengthBits + i] != hashBits[i]:
                raise ValueError('Failed checksum.')
        return entropy

    def to_mnemonic(self, data):
        if len(data) not in [16, 20, 24, 28, 32]:
            raise ValueError('Data length should be one of the following: [16, 20, 24, 28, 32], but it is not (%d).' % len(data))
        h = hashlib.sha256(data).hexdigest()
        b = bin(int(binascii.hexlify(data), 16))[2:].zfill(len(data) * 8) + \
            bin(int(h, 16))[2:].zfill(256)[:len(data) * 8 // 32]
        result = []
        for i in range(len(b) // 11):
            idx = int(b[i * 11:(i + 1) * 11], 2)
            result.append(self.wordlist[idx])
        return self.joiner.join(result)

    def check(self, mnemonic):
        mnemonic = Mnemonic.normalize_string(mnemonic).split(u' ')
        if len(mnemonic) % 3 > 0:
            return False
        try:
            idx = map(lambda x: bin(self.wordlist.index(x))[2:].zfill(11), mnemonic)
            b = ''.join(idx)
        except:
            return False
        l = len(b)
        d = b[:l // 33 * 32]
        h = b[-l // 33:]
        nd = binascii.unhexlify(hex(int(d, 2))[2:].rstrip('L').zfill(l // 33 * 8))
        nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[:l // 33]
        return h == nh

    def expand_word(self, prefix):
        if prefix in self.wordlist:
            return prefix
        else:
            matches = [word for word in self.wordlist if word.startswith(prefix)]
            if len(matches) == 1: # matched exactly one word in the wordlist
                return matches[0]
            else:
                # exact match not found.
                # this is not a validation routine, just return the input
                return prefix

    def expand(self, mnemonic):
        return self.joiner.join([self.expand_word(word) for word in Mnemonic.normalize_string(mnemonic).split(u' ')])

    @classmethod
    def to_seed(cls, mnemonic, passphrase=''):
        mnemonic = cls.normalize_string(mnemonic)
        passphrase = cls.normalize_string(passphrase)
        return PBKDF2(mnemonic, u'mnemonic' + passphrase, iterations=PBKDF2_ROUNDS, macmodule=hmac, digestmodule=hashlib.sha512).read(64)


def main():
    import binascii
    import sys
    if len(sys.argv) > 1:
        data = sys.argv[1]
    else:
        data = sys.stdin.readline().strip()
    data = binascii.unhexlify(data)
    m = Mnemonic('english')
    print(m.to_mnemonic(data))


if __name__ == '__main__':
    main()

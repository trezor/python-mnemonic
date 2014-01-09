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

import os
import hashlib
import hmac
import binascii
from pbkdf2 import PBKDF2

PBKDF2_ROUNDS = 2048

class Mnemonic(object):
	def __init__(self, language):
		self.radix = 2048
		self.wordlist = [w.strip() for w in open('%s/%s.txt' % (self._get_directory(), language), 'r').readlines()]
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist should contain %d words, but it contains %d words.' % (self.radix, len(self.wordlist)))

	@classmethod
	def _get_directory(cls):
		return os.path.join(os.path.dirname(__file__), 'wordlist')

	@classmethod
	def list_languages(cls):
		return [ f.split('.')[0] for f in os.listdir(cls._get_directory()) if f.endswith('.txt') ]

	@classmethod
	def detect_language(cls, code):
		first = code.split(' ')[0]
		languages = cls.list_languages()

		for lang in languages:
			mnemo = cls(lang)
			if first in mnemo.wordlist:
				return lang

		raise Exception("Language not detected")

	def generate(self, strength = 128):
		if strength % 32 > 0:
			raise Exception('Strength should be divisible by 32, but it is not (%d).' % strength)
		return self.to_mnemonic(os.urandom(strength / 8))

	def to_mnemonic(self, data):
		if len(data) % 4 > 0:
			raise Exception('Data length in bits should be divisible by 32, but it is not (%d bytes = %d bits).' % (len(data), len(data) * 8))
		h = hashlib.sha256(data).hexdigest()
		b = bin(int(binascii.hexlify(data), 16))[2:].zfill(len(data) * 8) + \
		    bin(int(h, 16))[2:].zfill(256)[:len(data) * 8 / 32]
		result = []
		for i in range(len(b) / 11):
			idx = int(b[i * 11:(i + 1) * 11], 2)
			result.append(self.wordlist[idx])
		return ' '.join(result)

	def check(self, mnemonic):
		mnemonic = mnemonic.split(' ')
		if len(mnemonic) % 3 > 0:
			return False
		try:
			idx = map(lambda x: bin(self.wordlist.index(x))[2:].zfill(11), mnemonic)
		except:
			return False
		b = ''.join(idx)
		l = len(b)
		d = b[:l / 33 * 32]
		h = b[-l / 33:]
		nd = binascii.unhexlify(hex(int(d, 2))[2:].rstrip('L').zfill(l / 33 * 8))
		nh = bin(int(hashlib.sha256(nd).hexdigest(), 16))[2:].zfill(256)[:l / 33]
		return h == nh

	@classmethod
	def to_seed(cls, mnemonic, passphrase = ''):
		return PBKDF2(mnemonic, 'mnemonic' + passphrase, iterations = PBKDF2_ROUNDS, macmodule = hmac, digestmodule = hashlib.sha512).read(64)

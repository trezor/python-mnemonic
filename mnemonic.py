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
# The code is inspired by Electrum mnemonic code by ThomasV
#

import struct
import binascii
import os

class Mnemonic(object):
	directory = 'wordlist'

	def __init__(self, language):
		self.radix = 2048
		self.wordlist = [w.strip() for w in open('%s/%s.txt' % (self.directory, language), 'r').readlines()]
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist should contain %d words.' % self.radix)

	@classmethod
	def list_languages(cls):
		return [ f.split('.')[0] for f in os.listdir(cls.directory) ]

	@classmethod
	def detect_language(cls, code):
		first = code.split(' ')[0]
		languages = cls.list_languages()

		for lang in languages:
			mnemo = cls(lang)
			if first in mnemo.wordlist:
				return lang

		raise Exception("Language not detected")

	def checksum(self, b):
		l = len(b) / 32
		c = 0
		for i in range(32):
			c ^= int(b[i * l:(i + 1) * l], 2)
		c = bin(c)[2:].zfill(l)
		return c

	def encode(self, data):
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist does not contain %d items!' % self.radix)
		if len(data) % 4 != 0:
			raise Exception('Data length not divisable by 4!')
		b = bin(int(binascii.hexlify(data), 16))[2:].zfill(len(data) * 8)
		assert len(b) % 32 == 0
		c = self.checksum(b)
		assert len(c) == len(b) / 32
		e = b + c
		assert len(e) % 33 == 0
		result = []
		for i in range(len(e) / 11):
			idx = int(e[i * 11:(i + 1) * 11], 2)
			result.append(self.wordlist[idx])
		return ' '.join(result)

	def decode(self, code):
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist does not contain %d items!' % self.radix)
		code = [w for w in code.split(' ') if w]
		if len(code) % 3 != 0:
			raise Exception('Mnemonic code length not divisible by 3!')
		e = [ bin(self.wordlist.index(w))[2:].zfill(11) for w in code ]
		e = ''.join(e)
		l = len(e)
		assert l % 33 == 0
		b = e[:l / 33 * 32]
		c = e[l / 33 * 32:]
		assert len(b) % 32 == 0
		assert len(c) == len(b) / 32
		if self.checksum(b) != c:
			raise Exception('Mnemonic checksum error')
		b = hex(int(b, 2))[2:].rstrip('L').zfill(len(b)/4)
		return binascii.unhexlify(b)

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
# Note about US patent no 5892470:
# In our implementation the mnemonic word depends on the previous words.
# In the original patent, the word choice is independent from the previous words.
#

import struct

class Mnemonic(object):

	def __init__(self):
		self.radix = 2048
		self.wordlist = [w.strip() for w in open('wordlist/english.txt', 'r').readlines()]
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist should contain %d words.' % self.radix)

	def paritybit(self, num):
		return bin(num).count('1') % 2

	def encode(self, data):
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist does not contain %d items!' % self.radix)
		if len(data) % 4 != 0:
			raise Exception('Data length not divisable by 4!')
		result = []
		for i in range(len(data)/4):
			num = (struct.unpack_from('>I', data, 4*i)[0]) & 0xFFFFFFFF
			num |= self.paritybit(num) << 32
			w1 = (num) % self.radix
			w2 = ((num / self.radix) + w1) % self.radix
			w3 = ((num / self.radix / self.radix) + w2) % self.radix
			result += [ self.wordlist[w1], self.wordlist[w2], self.wordlist[w3] ]
		return ' '.join(result)

	def decode(self, code):
		if len(self.wordlist) != self.radix:
			raise Exception('Wordlist does not contain %d items!' % self.radix)
		code = [w for w in code.split(' ') if w]
		if len(code) % 3 != 0:
			raise Exception('Mnemonic code length not divisible by 3!')
		result = ''
		for i in range(len(code)/3):
			word1, word2, word3 = code[3*i : 3*(i+1)]
			w1 = self.wordlist.index(word1)
			w2 = self.wordlist.index(word2)
			w3 = self.wordlist.index(word3)
			num = (w1 % self.radix + self.radix * ((w2 - w1) % self.radix) + self.radix * self.radix * ((w3 - w2) % self.radix))
			if self.paritybit(num & 0xFFFFFFFF) != (num >> 32):
				raise Exception('Mnemonic code checksum mismatch')
			result += struct.pack('>I', num & 0xFFFFFFFF)
		return result

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

import struct

class Mnemonic(object):

	def __init__(self):
		self.adj = [w.strip() for w in open('words/bip0039_adj.txt', 'r').readlines()]
		self.adv = [w.strip() for w in open('words/bip0039_adv.txt', 'r').readlines()]
		self.noun = [w.strip() for w in open('words/bip0039_noun.txt', 'r').readlines()]
		self.verb = [w.strip() for w in open('words/bip0039_verb.txt', 'r').readlines()]
		if len(self.adj) != 2048:
			raise Exception('Adjectives wordlist should contain 1024 words.')
		if len(self.adv) != 1024:
			raise Exception('Adverbs wordlist should contain 1024 words.')
		if len(self.noun) != 2048:
			raise Exception('Nouns wordlist should contain 1024 words.')
		if len(self.verb) != 1024:
			raise Exception('Verbs wordlist should contain 1024 words.')

	def encode(self, data):
		if len(data) % 8 != 0:
			raise Exception('Data length not divisable by 8 (64 bits)!')
		result = []
		for i in range(len(data)/8):
			num = (struct.unpack_from('>Q', data, 8*i)[0]) & 0xFFFFFFFFFFFFFFFF
			result.append(self.adj[(num >> 53) & 0x7FF])
			result.append(self.noun[(num >> 42) & 0x7FF])
			result.append(self.adv[(num >> 32) & 0x3FF])
			result.append(self.verb[(num >> 22) & 0x3FF])
			result.append(self.adj[(num >> 11) & 0x7FF])
			result.append(self.noun[num & 0x7FF] + '.')
		return ' '.join(result)

	def decode(self, code):
		code = [w.rstrip('.') for w in code.split(' ') if w]
		if len(code) % 3 != 0:
			raise Exception('Mnemonic code length not divisible by 6!')
		result = ''
		for i in range(len(code)/6):
			word1, word2, word3, word4, word5, word6 = code[6*i : 6*(i+1)]
			w1 = self.adj.index(word1)
			w2 = self.noun.index(word2)
			w3 = self.adv.index(word3)
			w4 = self.verb.index(word4)
			w5 = self.adj.index(word5)
			w6 = self.noun.index(word6)
			num = (w1 << 53) + (w2 << 42) + (w3 << 32) + (w4 << 22) + (w5 << 11) + w6
			result += struct.pack('>Q', num)
		return result

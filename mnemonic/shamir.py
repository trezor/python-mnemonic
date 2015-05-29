#
# Copyright (c) 2015 Pavol Rusnak
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

from mnemonic import Mnemonic
from secretsharing import SecretSharer
import binascii

class Shamir(object):
	def __init__(self, language):
		self.mnemo = Mnemonic(language)

	def split(self, data, m, n):
		if len(data) != 30:
			raise Exception('Data length is not 240 bits')
		if m < 2 or m > 15:
			raise Exception('Invalid M provided')
		if n < 2 or n > 15:
			raise Exception('Invalid N provided')
		return [ '8%x%x%s%s' % (m, n, x[0], x[2:]) for x in SecretSharer.split_secret(binascii.hexlify(data), m, n) ]

	def combine(self, shares):
		shares = [ '%s-%s' % (x[3], x[4:]) for x in shares ]
		r = SecretSharer.recover_secret(shares)
		return binascii.unhexlify(r)

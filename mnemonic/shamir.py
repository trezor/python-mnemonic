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
from secretsharing import secret_int_to_points, points_to_secret_int
import binascii

# see https://primes.utm.edu/lists/2small/ for biggest primes that fit into X bits

# 12 words
# DATALEN = (16 - 1)       # 120 bits
# PRIME   = (2**120 - 119) # biggest prime that fits into 120 bits

# 15 words
DATALEN = (20 - 1)       # 152 bits
PRIME   = (2**152 - 17)  # biggest prime that fits into 152 bits

# 18 words
# DATALEN = (24 - 1)       # 184 bits
# PRIME   = (2**184 - 33)  # biggest prime that fits into 184 bits

# 21 words
# DATALEN = (28 - 1)       # 216 bits
# PRIME   = (2**216 - 377) # biggest prime that fits into 216 bits

# 24 words
# DATALEN = (32 - 1)       # 248 bits
# PRIME   = (2**248 - 237) # biggest prime that fits into 248 bits

class Shamir(object):

	def __init__(self, language):
		self.mnemo = Mnemonic(language)

	def split(self, data, m, n):
		if len(data) != DATALEN:
			raise Exception('Data length should be %d bits, not %d bits.' % (DATALEN * 8, len(data) * 8))
		if m < 2 or m > 15:
			raise Exception('Invalid M provided')
		if n < 2 or n > 15:
			raise Exception('Invalid N provided')
		s = secret_int_to_points(int(binascii.hexlify(data), 16), m, n, PRIME)
		s = [ '%x%x%s' % (m, x[0], ('%x' % x[1]).zfill(DATALEN * 2)) for x in s ]
		return [ self.mnemo.to_mnemonic(binascii.unhexlify(x)) for x in s ]

	def combine(self, shares):
		shares = [ binascii.hexlify(self.mnemo.to_entropy(x)) for x in shares ]
		if set([ int(x[0], 16) for x in shares ]) != set([len(shares)]):
			raise Exception('Shares do not match needed threshold')
		points = [ ( int(x[1], 16), int(x[2:], 16) ) for x in shares ]
		r = points_to_secret_int(points, PRIME)
		r = hex(r)[2:-1].zfill(DATALEN * 2)
		return binascii.unhexlify(r)

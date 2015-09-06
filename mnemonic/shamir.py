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
from .secretsharing import secret_int_to_points, points_to_secret_int
import binascii

class Shamir(object):

	def __init__(self, language):
		self.mnemo = Mnemonic(language)
		# see https://primes.utm.edu/lists/2small/ for biggest primes that fit into X bits
		self.primes = {
			15: (2**120 - 119),
			19: (2**152 - 17),
			23: (2**184 - 33),
			27: (2**216 - 377),
			31: (2**248 - 237)
		}

	def split(self, data, m, n):
		if not len(data) in self.primes.keys():
			raise Exception('Unknown data length')
		if m < 2 or m > 15:
			raise Exception('Invalid M provided')
		if n < 2 or n > 15:
			raise Exception('Invalid N provided')
		prime = self.primes[len(data)]
		s = secret_int_to_points(int(binascii.hexlify(data), 16), m, n, prime)
		s = [ '%x%x%s' % (m, x[0], ('%x' % x[1]).zfill(len(data) * 2)) for x in s ]
		return [ self.mnemo.to_mnemonic(binascii.unhexlify(x)) for x in s ]

	def combine(self, shares):
		words = set([ len(x.split(' ')) for x in shares ])
		if len(words) != 1:
			raise Exception('Inconsistent number of words')
		datalen = list(words)[0] * 4 / 3 - 1
		shares = [ binascii.hexlify(self.mnemo.to_entropy(x)) for x in shares ]
		if set([ int(x[0], 16) for x in shares ]) != set([len(shares)]):
			raise Exception('Number of shares does not match the threshold')
		points = [ ( int(x[1], 16), int(x[2:], 16) ) for x in shares ]
		prime = self.primes[datalen]
		r = points_to_secret_int(points, prime)
		r = hex(r)[2:-1].zfill(datalen * 2)
		return binascii.unhexlify(r)

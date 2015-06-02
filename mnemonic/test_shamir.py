#!/usr/bin/python
from shamir import Shamir
import sys

def shamir_test(m, n):
	s = Shamir('english')
	seed = "Shamir for Mnemonic"
	shares = s.split(seed, m, n)
	print 'original:', seed
	print 'shares:'
	for i in range(len(shares)):
		print '%2d :' % (i + 1), shares[i]
	shares = shares[:m] # take first m shares
	cmb = s.combine(shares)
	print 'combined:', cmb
	if seed == cmb:
		print 'TEST OK'
		print
	else:
		print 'TEST FAILED !!!'
		sys.exit(1)

for n in range(2, 15 + 1):
	for m in range(2, n + 1):
		shamir_test(m, n)

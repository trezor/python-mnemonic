#!/usr/bin/python

from shamir import Shamir

s = Shamir('english')

seed = "Shamir for Mnemonic"

shares = s.split(seed, 15, 15)

print

print 'original:', seed

print

print 'shares:'

print

for i in range(len(shares)):
    print '%2d :' % (i + 1), shares[i]

cmb = s.combine(shares)

print

print 'combined:', cmb

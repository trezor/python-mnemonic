#!/usr/bin/python

from shamir import Shamir

s = Shamir('english')

shares = s.split('heh' * 10, 15, 15)

print shares

c = s.combine(shares)

print

print c

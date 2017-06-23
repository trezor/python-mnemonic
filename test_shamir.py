#!/usr/bin/env python
from __future__ import print_function
import sys
from mnemonic.shamir import Shamir


def shamir_test(l, m, n):
    s = Shamir('english')
    seed = b"Shamir's Secret Sharing Scheme!"[:l]  # take first l characters
    shares = s.split(seed, m, n)
    print('original:', seed)
    print('shares:')
    for i, sh in enumerate(shares):
        print('%2d :' % (i + 1), sh)
    shares = shares[:m]  # take first m shares
    cmb = s.combine(shares)
    print('combined:', cmb)
    if seed == cmb:
        print('TEST OK')
        print()
    else:
        print('TEST FAILED !!!')
        sys.exit(1)


for l in [15, 19, 23, 27, 31]:
    for n in range(2, 15 + 1):
        for m in range(2, n + 1):
            shamir_test(l, m, n)

#!/usr/bin/env python

from __future__ import print_function

import json
import sys
from binascii import hexlify, unhexlify
from random import choice, seed
from bip32utils import BIP32Key

from mnemonic import Mnemonic

def b2h(b):
    h = hexlify(b)
    return h if sys.version < '3' else h.decode('utf8')

def process(data, lst):
    code = mnemo.to_mnemonic(unhexlify(data))
    seed = Mnemonic.to_seed(code, passphrase='TREZOR')
    xprv = BIP32Key.fromEntropy(seed).ExtendedKey()
    seed = b2h(seed)
    print('input    : %s (%d bits)' % (data, len(data) * 4))
    print('mnemonic : %s (%d words)' % (code, len(code.split(' '))))
    print('seed     : %s (%d bits)' % (seed, len(seed) * 4))
    print('xprv     : %s' % xprv)
    print()
    lst.append((data, code, seed, xprv))

if __name__ == '__main__':
    out = {}
    seed(1337)

    for lang in ['english']: # Mnemonic.list_languages():
        mnemo = Mnemonic(lang)
        out[lang] = []

        # Generate corner cases
        data = []
        for l in range(16, 32 + 1, 8):
            for b in ['00', '7f', '80', 'ff']:
                process(b * l, out[lang])

        # Generate random seeds
        for i in range(12):
            data = ''.join(chr(choice(range(0, 256))) for _ in range(8 * (i % 3 + 2)))
            if sys.version >= '3':
                data = data.encode('latin1')
            process(b2h(data), out[lang])

    with open('vectors.json', 'w') as f:
        json.dump(out, f, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

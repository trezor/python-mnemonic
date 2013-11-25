#!/usr/bin/python
import json
from binascii import hexlify, unhexlify
from random import choice
from mnemonic import Mnemonic

def process(data, lst):
    code = mnemo.to_mnemonic(unhexlify(data))
    seed = hexlify(Mnemonic.to_seed(code, passphrase = 'TREZOR'))
    print 'input    : %s (%d bits)' % (data, len(data) * 4)
    print 'mnemonic : %s (%d words)' % (code, len(code.split(' ')))
    print 'seed     : %s (%d bits)' % (seed, len(data) * 4)
    print
    lst.append((data, code, seed))

if __name__ == '__main__':
    out = {}

    for lang in Mnemonic.list_languages():
        mnemo = Mnemonic(lang)
        out[lang] = []

        # Generate corner cases
        data = []
        for l in range(16, 32 + 1, 8):
            for b in ['00', '7f', '80', 'ff']:
                process(b * l, out[lang])

        # Generate random seeds
        for i in range(12):
            data = hexlify(''.join(chr(choice(range(0, 256))) for _ in range(8 * (i % 3 + 2))))
            process(data, out[lang])

    json.dump(out, open('vectors.json', 'w'), sort_keys=True, indent=4,)

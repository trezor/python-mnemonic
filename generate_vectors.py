#!/usr/bin/python
import json
from binascii import hexlify, unhexlify
from random import choice
from mnemonic import Mnemonic

if __name__ == '__main__':
    out = {}

    for lang in Mnemonic.list_languages():
        mnemo = Mnemonic(lang)
        out[lang] = []

        # Generate corner cases
        data = []
        for l in range(8, 32 + 1, 8):
            for b in ['00', '7f', '80', 'ff']:
                data = (b * l)
                code = mnemo.encode(unhexlify(data))

                print 'input    : %s (%d bits)' % (data, len(data) * 4)
                print 'mnemonic : %s (%d words)' % (code, len(code.split(' ')))

                out[lang].append((data, code))

        # Generate random seeds
        for i in range(12):
            data = ''.join(chr(choice(range(0, 256))) for _ in range(8 * (i % 3 + 2)))
            print 'input    : %s (%d bits)' % (hexlify(data), len(data) * 8)
            code = mnemo.encode(data)
            print 'mnemonic : %s (%d words)' % (code, len(code.split(' ')))
            print

            out[lang].append((hexlify(data), code))

    json.dump(out, open('vectors.json', 'w'), sort_keys=True, indent=4,)


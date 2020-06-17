#!/usr/bin/env python3

import json
from random import choice, seed

from bip32utils import BIP32Key
from mnemonic import Mnemonic


def process(data, lst):
    code = mnemo.to_mnemonic(bytes.fromhex(data))
    seed = Mnemonic.to_seed(code, passphrase="TREZOR")
    xprv = BIP32Key.fromEntropy(seed).ExtendedKey()
    seed = seed.hex()
    print("input    : %s (%d bits)" % (data, len(data) * 4))
    print("mnemonic : %s (%d words)" % (code, len(code.split(" "))))
    print("seed     : %s (%d bits)" % (seed, len(seed) * 4))
    print("xprv     : %s" % xprv)
    print()
    lst.append((data, code, seed, xprv))


if __name__ == "__main__":
    out = {}
    seed(1337)

    for lang in ["english"]:  # Mnemonic.list_languages():
        mnemo = Mnemonic(lang)
        out[lang] = []

        # Generate corner cases
        data = []
        for length in range(16, 32 + 1, 8):
            for b in ["00", "7f", "80", "ff"]:
                process(b * length, out[lang])

        # Generate random seeds
        for i in range(12):
            data = "".join(chr(choice(range(0, 256))) for _ in range(8 * (i % 3 + 2)))
            data = data.encode("latin1")
            process(data.hex(), out[lang])

    with open("vectors.json", "w") as f:
        json.dump(
            out, f, sort_keys=True, indent=4, separators=(",", ": "), ensure_ascii=False
        )

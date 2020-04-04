#!/usr/bin/env python

from binascii import hexlify, unhexlify
from mnemonic import Mnemonic
import random
import sys

seeds_peers =  {"12": 128, '18':192, '24':256}
length = "12"
if len(sys.argv) > 1:
    length = sys.argv[1]
    if length not in seeds_peers.keys():
        print("Seeds length should be one of the following: [12, 18, 24], but it is not "+length)
        sys.exit(0)
key_bits_length = seeds_peers[length]
code_length = int(key_bits_length / 4)
mnemo = Mnemonic("english")
key_hexstr =""
for _ in range(code_length):
    key_hexstr += random.sample("ABCDEF0123456789",1)[0]

print("\n seeds[12*/18/24]:"+length)
print("\n  "+mnemo.to_mnemonic(unhexlify(key_hexstr)))
print("\n key_bits[128/192/256]:"+str(key_bits_length))
print("\n  "+key_hexstr)


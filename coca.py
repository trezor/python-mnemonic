#!/usr/bin/python
#
# Copyright (c) 2013 Aaron Voisine
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# This code takes the 5000 most frequent word list from the Corpus of
# Contemporary American English (COCA), and outputs the BIP 39 english word list

import re

cocalist = []
electrumlist = []
bip39enlist = []
remove = ['fucking', 'shit', 'hell', 'damn', 'ass', 'butt', 'sex', 'sexual',
          'sexually', 'sexy', 'sexuality', 'abortion', 'cocaine', 'vs', 'ie',
          're', 'uh', 'ha']

with open('words/COCA.txt', 'r') as f:
    cocalist = [line.strip() for line in f.readlines()]

with open('words/electrum.txt', 'r') as f:
    electrumlist = [line.strip() for line in f.readlines()]

regex = re.compile('^[a-z]+$')

for w in cocalist:
    if len(w) > 10: continue
    if not regex.match(w): continue
    if w in electrumlist: continue
    if w in bip39enlist: continue
    if w in remove: continue

    l = [w2 for w2 in bip39enlist if w2[:4] == w[:4]]

    if l:
        if len(w) >= len(l[0]): continue
        bip39enlist.remove(l[0])

    bip39enlist.append(w)
    if len(bip39enlist) >= 1626: break

for w in bip39enlist:
    print w
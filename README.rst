python-mnemonic
===============

.. image:: https://travis-ci.org/trezor/python-mnemonic.svg?branch=master
    :target: https://travis-ci.org/trezor/python-mnemonic

Reference implementation of BIP-0039: Mnemonic code for generating
deterministic keys

Abstract
--------

This BIP describes the implementation of a mnemonic code or mnemonic sentence --
a group of easy to remember words -- for the generation of deterministic wallets.

It consists of two parts: generating the mnenomic, and converting it into a
binary seed. This seed can be later used to generate deterministic wallets using
BIP-0032 or similar methods.

BIP Paper
---------

See https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
for full specification

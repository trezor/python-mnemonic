python-mnemonic
===============

.. image:: https://badge.fury.io/py/mnemonic.svg
    :target: https://badge.fury.io/py/mnemonic

Reference implementation of BIP-0039: Mnemonic code for generating
deterministic keys

Maintained by `Trezor <https://trezor.io>`_. See the `GitHub repository <https://github.com/trezor/python-mnemonic>`_ for source code and issue tracking.

Abstract
--------

This BIP describes the implementation of a mnemonic code or mnemonic sentence --
a group of easy to remember words -- for the generation of deterministic wallets.

It consists of two parts: generating the mnemonic, and converting it into a
binary seed. This seed can be later used to generate deterministic wallets using
BIP-0032 or similar methods.

BIP Paper
---------

See `BIP-0039`_ for the full specification.

Installation
------------

To install this library and its dependencies use:

.. code-block:: sh

   $ pip install mnemonic

Usage examples
--------------

Import library into python project via:

.. code-block:: python

   from mnemonic import Mnemonic

Initialize class instance, picking from available dictionaries:

- english
- chinese_simplified
- chinese_traditional
- french
- italian
- japanese
- korean
- spanish
- turkish
- czech
- portuguese

.. code-block:: python

   mnemo = Mnemonic(language)
   mnemo = Mnemonic("english")

Generate word list given the strength (128 - 256):

.. code-block:: python

   words = mnemo.generate(strength=256)

Given the word list and custom passphrase (empty in example), generate seed:

.. code-block:: python

   seed = mnemo.to_seed(words, passphrase="")

Given the word list, calculate original entropy:

.. code-block:: python

   entropy = mnemo.to_entropy(words)

Command-line interface
----------------------

The ``mnemonic`` command provides CLI access to the library:

.. code-block:: sh

   $ mnemonic create --help
   $ mnemonic check --help
   $ mnemonic to-seed --help

Generate a new mnemonic phrase:

.. code-block:: sh

   $ mnemonic create
   $ mnemonic create -s 256 -l english -p "my passphrase"
   $ mnemonic create -s 256 -l english
   $ mnemonic create -P                  # prompt for passphrase (hidden input)
   $ mnemonic create --hide-seed         # only output mnemonic, not the seed
   $ MNEMONIC_PASSPHRASE="secret" mnemonic create

Validate a mnemonic phrase:

.. code-block:: sh

   $ mnemonic check abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
   $ echo "abandon abandon ..." | mnemonic check

Derive seed from a mnemonic phrase:

.. code-block:: sh

   $ mnemonic to-seed abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
   $ mnemonic to-seed -p "my passphrase" word1 word2 ...
   $ mnemonic to-seed -P word1 word2 ...   # prompt for passphrase (hidden input)
   $ MNEMONIC_PASSPHRASE="secret" mnemonic to-seed word1 word2 ...

.. _BIP-0039: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

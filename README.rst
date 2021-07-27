python-mnemonic
===============

.. image:: https://badge.fury.io/py/mnemonic.svg
    :target: https://badge.fury.io/py/mnemonic

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

Installation
------------

To install this library and its dependencies use:

 ``pip install mnemonic``

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

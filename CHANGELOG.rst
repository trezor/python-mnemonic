Changelog
=========

.. default-role:: code

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to
`Semantic Versioning`_.

`0.21`_ - 2024-01-05
--------------------

.. _0.21: https://github.com/trezor/python-mnemonic/compare/v0.20...v0.21

Added
~~~~~

- Czech and Portuguese wordlists
- Option to provide custom list of words instead of loading from built-in file

Changed
~~~~~~~

- Use `secrets` module for randomness
- Use English as a default language if none is provided
- Language detection is unambiguous even if some words are ambiguous
- Build system switched to Poetry

Removed
~~~~~~~

- Support for Python below 3.8 was dropped


`0.20`_ - 2021-07-27
---------------------

.. _0.20: https://github.com/trezor/python-mnemonic/compare/v0.19...v0.20

Added
~~~~~

- Type annotations
- Support for testnet private keys

Changed
~~~~~~~

- Project directory structure was cleaned up
- Language on the `Mnemonic` object is remembered instead of repeatedly detecting

Removed
~~~~~~~

- Support for Python 2.7 and 3.4 was dropped



0.19 - 2019-10-01
------------------

Added
~~~~~

- Start of changelog


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

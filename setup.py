#!/usr/bin/env python
from setuptools import setup

#python setup.py sdist upload

setup(name='mnemonic',
      version='0.1',
      description='Implementation of Bitcoin BIP-0039',
      author='Bitcoin TREZOR',
      author_email='info@bitcointrezor.com',
      url='https://github.com/trezor/python-mnemonic',
      packages=['mnemonic', 'pbkdf2'],
      package_data={'mnemonic': ['wordlist/*.txt']},
      zip_safe=False,
      install_requires=[],
     )

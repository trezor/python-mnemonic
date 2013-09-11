#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

#python setup.py sdist upload

from setuptools import setup
from stratum import version

setup(name='mnemonic',
      version='0.3',
      description='Implementation of Bitcoin BIP0039',
      author='slush',
      author_email='info@bitcoin.cz',
      url='https://github.com/trezor/python-mnemonic',
      packages=['mnemonic',],
      package_data={'mnemonic': ['wordlist/*.txt']},
      zip_safe=False,
      install_requires=[],
     )

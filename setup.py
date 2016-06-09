#!/usr/bin/env python
from setuptools import setup

setup(
    name='mnemonic',
    version='0.14',
    author='Bitcoin TREZOR',
    author_email='info@bitcointrezor.com',
    description='Implementation of Bitcoin BIP-0039',
    url='https://github.com/trezor/python-mnemonic',
    packages=['mnemonic',],
    package_data={'mnemonic': ['wordlist/*.txt']},
    zip_safe=False,
    install_requires=['pbkdf2'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
    ],
)

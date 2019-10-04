#!/usr/bin/env python
from setuptools import setup

setup(
    name="mnemonic",
    version="0.19",
    author="Trezor",
    author_email="info@trezor.io",
    description="Implementation of Bitcoin BIP-0039",
    url="https://github.com/trezor/python-mnemonic",
    packages=["mnemonic"],
    package_data={"mnemonic": ["wordlist/*.txt"]},
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
    ],
)

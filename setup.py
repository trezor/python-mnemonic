#!/usr/bin/env python3
from pathlib import Path
import os
from setuptools import setup

CWD = Path(__file__).resolve().parent


setup(
    name="mnemonic",
    version="0.19",
    author="Trezor",
    author_email="info@trezor.io",
    description="Implementation of Bitcoin BIP-0039",
    long_description="\n".join(
        (CWD / "README.rst").read_text(),
        (CWD / "CHANGELOG.rst").read_text(),
    ),
    url="https://github.com/trezor/python-mnemonic",
    packages=["mnemonic"],
    package_data={"mnemonic": ["wordlist/*.txt", "py.typed"]},
    zip_safe=False,
    python_requires=">=3.5",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
    ],
)

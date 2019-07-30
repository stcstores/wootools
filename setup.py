#!/usr/bin/env python
"""Setup for wootools."""

from pathlib import Path

import setuptools

NAME = "wootools"

with open("README.rst", "r") as readme:
    long_description = readme.read()

here = Path(__file__).parent

about = {}
with open(here / NAME / "__version__.py", "r") as f:
    exec(f.read(), about)

setuptools.setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    install_requires=["tabler", "click"],
    packages=setuptools.find_packages(),
    entry_points="""
        [console_scripts]
        wootools=wootools.cli:cli
    """,
)

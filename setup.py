#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from codecs import open

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "Readme.md"), encoding="utf-8") as f:
    readme = f.read()


def build():
    os.system("python3 setup.py sdist bdist_wheel")


def publish():
    os.system("twine upload dist/*")


if sys.argv[-1] == "build":
    build()
    sys.exit()
elif sys.argv[-1] == "publish":
    build()
    publish()
    sys.exit()
elif sys.argv[-1] == "publish-only":
    publish()
    sys.exit()


packages = [
    "feedsearch_crawler",
    "feedsearch_crawler.crawler",
    "feedsearch_crawler.feed_spider",
]

required = [
    "aiohttp",
    "beautifulsoup4",
    "feedparser",
    "cchardet",
    "aiodns",
    "w3lib",
    "uvloop ; sys_platform != 'win32'",
]

setup(
    name="feedsearch-crawler",
    version="1.0.0",
    description="Search sites for RSS, Atom, and JSON feeds",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="David Beath",
    author_email="davidgbeath@gmail.com",
    url="https://github.com/DBeath/feedsearch-crawler",
    license="MIT",
    packages=packages,
    install_requires=required,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Typing :: Typed",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.7",
)

#!/usr/bin/env python
#
# Copywright (C) 2024 Debmalya Pramanik
# LICENSE: MIT License

from setuptools import setup
from setuptools import find_packages

import routicle as ro

setup(
    name = "pandas-wizard",
    version = ro.__version__,
    author = "DigitPhilia INC. Developers",
    author_email = "john.doe@example.com",
    description = "Inventory Planning, Stock Routing and Optimization",
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/digitphilia/routicle",
    packages = find_packages(),
    classifiers = [
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License"
    ],
    project_urls = {
        "Issue Tracker" : "https://github.com/digitphilia/routicle/issues",
        "Code Documentations" : "",
        "Org. Homepage" : "https://github.com/digitphilia"
    },
    keywords = [
        # main keywords for package indexing
        "optimization", "share of business", "linear programming",
        "integer programming", "mixed integer programming"
    ],
    python_requires = ">=3.10",

    # check package data details from manifest file
    include_package_data = True
)

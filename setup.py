#!/usr/bin/env python
# coding=utf-8
"""The regolith installer."""
from __future__ import print_function
import os
import sys

try:
    from setuptools import setup
    from setuptools.command.develop import develop

    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup

    HAVE_SETUPTOOLS = False

from regolith import __version__ as RG_VERSION


def main():
    try:
        if "--name" not in sys.argv:
            print(logo)
    except UnicodeEncodeError:
        pass
    with open(os.path.join(os.path.dirname(__file__), "README.rst"), "r") as f:
        readme = f.read()
    skw = dict(
        name="regolith",
        description="A research group content management system",
        long_description=readme,
        license="CC0",
        version='0.5.0',
        author="Anthony Scopatz",
        maintainer="Anthony Scopatz",
        author_email="scopatz@gmail.com",
        url="https://github.com/scopatz/regolith",
        platforms="Cross Platform",
        classifiers=["Programming Language :: Python :: 3"],
        packages=["regolith", "regolith.builders"],
        package_dir={"regolith": "regolith"},
        package_data={
            "regolith": [
                "templates/*",
                "static/*.*",
                "static/img/*.*",
                "*.xsh",
            ]
        },
        scripts=["scripts/regolith"],
        zip_safe=False,
    )
    if HAVE_SETUPTOOLS:
        skw["setup_requires"] = []
        # skw['install_requires'] = ['Jinja2', 'pymongo']
    setup(**skw)


logo = """
"""

if __name__ == "__main__":
    main()

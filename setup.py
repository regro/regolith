#!/usr/bin/env python
# coding=utf-8
"""The regolith installer."""
from __future__ import print_function
from pathlib import Path
import os
import sys
import platform

try:
    from setuptools import setup
    from setuptools.command.develop import develop

    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup

    HAVE_SETUPTOOLS = False

from regolith import __version__ as RG_VERSION
PW_AFFECTED_OSX_SYSTEMS = ["darwin"]

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
        version='0.8.2',
        author="Anthony Scopatz",
        maintainer="Anthony Scopatz",
        author_email="scopatz@gmail.com",
        url="https://github.com/scopatz/regolith",
        platforms="Cross Platform",
        python_requires='>=3.8',
        classifiers=["Programming Language :: Python :: 3"],
        packages=["regolith", "regolith.builders", "regolith.helpers"],
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

    if platform.system().lower() in PW_AFFECTED_OSX_SYSTEMS:
    #The following lines find the python.app script, parses the script to find the path of its executable, and sets
    #the sys.executable to that executable. The shebang line created will be that of the new sys.executable
        import subprocess
        py_app_path = subprocess.check_output('which python.app', shell=True)
        py_app_path = py_app_path.decode('utf-8')[:-1]
        py_app_contents = subprocess.check_output('cat ' + py_app_path, shell=True)
        py_app_contents = py_app_contents.decode('utf-8')
        new_sys_executable = py_app_contents.splitlines()[-1]
        new_sys_executable = new_sys_executable.split(' ')[0]
        sys.executable = new_sys_executable

    skw['scripts'] = skw['scripts'] + ['scripts/helper_gui'] + ['scripts/profile_regolith'] + ['scripts/profile_helper_gui']
    setup(**skw)


logo = """
"""

if __name__ == "__main__":
    main()

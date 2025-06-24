#!/usr/bin/env python
##############################################################################
#
# (c) 2024-2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Billinge Group members and community contributors.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/regro/regolith/graphs/contributors
#
# See LICENSE.rst for license information.
#
##############################################################################

from xonsh.main import setup

# package version
from regolith.version import __version__  # noqa

"""Python package for research group content management system."""

# silence the pyflakes syntax checker
assert __version__ or True

setup()
del setup

# Initialize the Xonsh environment
# # execer = Execer(config=None)
# # XSH.load(execer=execer)
# # xonsh.imphooks.install_import_hooks(execer=execer)
#
# del xonsh

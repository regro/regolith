#!/usr/bin/env python
##############################################################################
#
# (c) 2024-2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Pavol Juhas, Billinge Group members and community contributors.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/regro/regolith/graphs/contributors  # noqa: E501
#
# See LICENSE.rst for license information.
#
##############################################################################
"""Definition of __version__."""

#  We do not use the other three variables, but can be added back if needed.
#  __all__ = ["__date__", "__git_commit__", "__timestamp__", "__version__"]

# obtain version information
from importlib.metadata import version

__version__ = version("regolith")

# End of file

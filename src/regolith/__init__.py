#!/usr/bin/env python
##############################################################################
#
# (c) 2024 The Trustees of Columbia University in the City of New York.
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

"""Research Group Content Management System"""

# package version
from src.regolith.version import __version__

# silence the pyflakes syntax checker
assert __version__ or True

# End of file
def __version__():
    return None
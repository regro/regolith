#!/usr/bin/env python
##############################################################################
#
# regolith         by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2011-2024 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
##############################################################################

"""
Definition of __version__
"""

# obtain version information
from importlib.metadata import version

__version__ = version("regolith")

# End of file

#!/usr/bin/env python
##############################################################################
#
# regolith         by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2011 The Trustees of Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE_DANSE.txt for license information.
#
##############################################################################

"""
Definition of __version__, __date__, __timestamp__, __git_commit__.

Notes
-----
Variable `__gitsha__` is deprecated as of version 3.0.
Use `__git_commit__` instead.
"""

__all__ = ["__date__", "__git_commit__", "__timestamp__", "__version__"]

import os.path

from importlib.resources import files, as_file


# obtain version information from the version.cfg file
cp = dict(version="", date="", commit="", timestamp="0")
if __package__ is not None:
    ref = files(__package__) / "version.cfg"
    with as_file(ref) as fcfg:
        if not os.path.isfile(fcfg):  # pragma: no cover
            from warnings import warn

            warn("Package metadata not found.")
            fcfg = os.devnull
        with open(fcfg) as fp:
            kwords = [
                [w.strip() for w in line.split(" = ", 1)] for line in fp if line[:1].isalpha() and " = " in line
            ]
        assert all(w[0] in cp for w in kwords), "received unrecognized keyword"
        cp.update(kwords)
    del kwords

__version__ = cp["version"]
__date__ = cp["date"]
__git_commit__ = cp["commit"]
__timestamp__ = int(cp["timestamp"])

# TODO remove deprecated __gitsha__ in version 3.1.
__gitsha__ = __git_commit__

del cp

# End of file

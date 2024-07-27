# import xonsh.imphooks
# from xonsh.built_ins import XSH
# from xonsh.execer import Execer

from xonsh.main import setup

from regolith.version import __version__

"""A Research group database management system"""

# Silence the pyflakes syntax checker
assert __version__ or True

setup()
del setup

# Initialize the Xonsh environment
# # execer = Execer(config=None)
# # XSH.load(execer=execer)
# # xonsh.imphooks.install_import_hooks(execer=execer)
#
# del xonsh

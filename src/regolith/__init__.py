# stup import hooks
import xonsh.imphooks
from xonsh.built_ins import XSH
from xonsh.execer import Execer

from regolith.version import __version__

"""A Research group database management system"""

# silence the pyflakes syntax checker
assert __version__ or True


XSH.load(execer=Execer())
execer = XSH.execer
xonsh.imphooks.install_import_hooks(execer=execer)

del xonsh

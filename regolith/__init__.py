# stup import hooks
import xonsh.imphooks
from xonsh.built_ins import XSH

xonsh.imphooks.install_import_hooks(execer=None)

__version__ = '0.5.1'

del xonsh

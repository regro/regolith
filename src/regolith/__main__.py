"""Run regolith as ``python -m regolith``.

The Windows launchers start it this way, and a package that can be run
by name is what anybody would expect of one with a command of its own.
"""

from regolith.main import main

if __name__ == "__main__":
    main()

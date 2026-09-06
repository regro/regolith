"""Where the databases and their collection files live.

Kept apart from regolith.tools so that the database clients can work out
a path without importing the rest of it, which costs a quarter of a
second and reaches google's api client and habanero.
"""

import pathlib


def dbdirname(db, rc):
    """Get the directory that holds a database as a pathlib.Path.

    Parameters
    ----------
    db : dict
        The database description.  A remote database is cached under
        the build directory, a local one lives at its own ``url``.
    rc : RunControl
        The run control instance supplying ``builddir``.

    Returns
    -------
    pathlib.Path
        The directory of the database.  Building it with pathlib keeps
        the separators native, so a posix-style ``url`` read from the
        rc file does not leave mixed separators on Windows.
    """
    if db.get("local", False) is False:
        dbdir = pathlib.Path(rc.builddir) / "_dbs" / db["name"]
    else:
        dbdir = pathlib.Path(db["url"])
    return dbdir


def dbpathname(db, rc):
    """Get the directory that holds the collection files as a
    pathlib.Path.

    Parameters
    ----------
    db : dict
        The database description, supplying ``path`` relative to the
        database directory.
    rc : RunControl
        The run control instance supplying ``builddir``.

    Returns
    -------
    pathlib.Path
        The directory of the collection files.
    """
    dbpath = dbdirname(db, rc) / db["path"]
    return dbpath

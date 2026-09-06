"""Helps manage mongodb setup and connections."""

import subprocess
from contextlib import contextmanager
from pathlib import Path
from warnings import warn

try:
    import hglib
except ImportError:
    hglib = None

from regolith.chained_db import LazyChainedDB
from regolith.client_manager import ClientManager
from regolith.dbpaths import dbdirname


def _run_git(args, cwd, check=False):
    """Run a git command in a directory.

    Parameters
    ----------
    args : list of str
        The git arguments, without the leading ``git``.
    cwd : str or pathlib.Path
        The directory to run the command in.
    check : bool, optional
        The switch to raise ``subprocess.CalledProcessError`` when the
        command returns a non-zero code.  The default is False.

    Returns
    -------
    subprocess.CompletedProcess
        The completed git process.
    """
    return subprocess.run(["git"] + list(args), cwd=str(cwd), check=check)


def _run_first_git_success(arg_lists, cwd):
    """Run git commands in order until one of them succeeds.

    Parameters
    ----------
    arg_lists : list of list of str
        The candidate argument lists, each tried in turn until one
        returns zero.
    cwd : str or pathlib.Path
        The directory to run the commands in.

    Returns
    -------
    bool
        Whether one of the commands succeeded.
    """
    for args in arg_lists:
        if _run_git(args, cwd).returncode == 0:
            return True
    return False


def load_git_database(db, client, rc):
    """Loads a git database."""
    dbdir = dbdirname(db, rc)
    # get or update the database
    if dbdir.is_dir():
        _run_first_git_success(
            [["pull", "upstream", "master"], ["pull", "origin", "master"], ["pull"]],
            dbdir,
        )
    else:
        subprocess.run(["git", "clone", db["url"], str(dbdir)])
    if getattr(rc, "branch", None):
        branch = rc.branch
        _run_first_git_success([["checkout", branch], ["checkout", "-b", branch, "master"]], dbdir)

    # import all of the data
    client.load_database(db)


def load_hg_database(db, client, rc):
    """Loads an hg database."""
    if hglib is None:
        raise ImportError("hglib")
    dbdir = dbdirname(db, rc)
    # get or update the database
    if dbdir.is_dir():
        client = hglib.open(str(dbdir))
        client.pull(update=True, force=True)
    else:
        # Strip off three characters for hg+
        client = hglib.clone(db["url"][3:], str(dbdir))
    # import all of the data
    client.load_database(db)


def load_local_database(db, client, rc):
    """Loads a local database."""
    # make sure that we expand user stuff
    db["url"] = str(Path(db["url"]).expanduser())
    # import all of the data
    client.load_database(db)


def load_mongo_database(db, client):
    """Load a mongo database."""
    client.load_database(db)


def load_database(db, client, rc):
    """Loads a database."""
    if db["backend"] in ("mongo", "mongodb"):
        load_mongo_database(db, client)
        return
    url = db["url"]
    if url.startswith("git") or url.endswith(".git"):
        load_git_database(db, client, rc)
    elif url.startswith("hg+"):
        load_hg_database(db, client, rc)
    elif Path(url).expanduser().exists():
        load_local_database(db, client, rc)
    else:
        raise ValueError("Do not know how to load this kind of database: " "{}".format(db))


def dump_git_database(db, client, rc, force=False):
    """Dumps a git database."""
    dbdir = dbdirname(db, rc)
    # dump the data that changed
    to_add = client.dump_database(db, force=force)
    if not to_add:
        # nothing was modified, so there is nothing to commit or push
        return
    # update the repo
    for file in to_add:
        subprocess.check_call(["git", "add", file], cwd=dbdir)
    cmd = ["git", "commit", "-m", "regolith auto-commit"]
    try:
        subprocess.check_call(cmd, cwd=dbdir)
    except subprocess.CalledProcessError:
        warn("Could not git commit to " + str(dbdir), RuntimeWarning)
        return
    cmd = ["git", "push"]
    if hasattr(rc, "remote") and hasattr(rc, "branch"):
        cmd += [rc.remote, rc.branch]
    try:
        subprocess.check_call(cmd, cwd=dbdir)
    except subprocess.CalledProcessError:
        warn("Could not git push from " + str(dbdir), RuntimeWarning)
        return


def dump_hg_database(db, client, rc, force=False):
    """Dumps an hg database."""
    dbdir = dbdirname(db, rc)
    # dump the data that changed
    to_add = client.dump_database(db, force=force)
    if not to_add:
        # nothing was modified, so there is nothing to commit or push
        return
    # update the repo
    hgclient = hglib.open(dbdir)
    if len(hgclient.status(include=to_add, modified=True, unknown=True, added=True)) == 0:
        return
    hgclient.commit(message="regolith auto-commit", include=to_add, addremove=True)
    hgclient.push()


def dump_local_database(db, client, rc, force=False):
    """Dumps a local database."""
    # dump the data that changed
    client.dump_database(db, force=force)
    return


def dump_database(db, client, rc, force=False):
    """Dumps a database.

    Only the collections that were modified since they were loaded are
    written, unless ``force`` is set, so a command that reads without
    writing leaves the database files untouched.
    """
    # do not dump mongo db
    if db["backend"] in ("mongo", "mongodb"):
        return
    url = db["url"]
    if url.startswith("git") or url.endswith(".git"):
        dump_git_database(db, client, rc, force=force)
    elif url.startswith("hg+"):
        dump_hg_database(db, client, rc, force=force)
    elif Path(url).expanduser().exists():
        dump_local_database(db, client, rc, force=force)
    else:
        raise ValueError("Do not know how to dump this kind of database")


def open_dbs(rc, dbs=None):
    """Open the databases.

    Parameters
    ----------
    rc : RunControl instance
        The rc which has links to the dbs
    dbs: set or None, optional
        The databases to load. If None load all, defaults to None

    Returns
    -------
    client : {FileSystemClient, MongoClient}
        The database client
    """
    if dbs is None:
        dbs = []
    client = ClientManager(rc.databases, rc)
    client.open()
    for db in rc.databases:
        # if we only want to access some dbs and this db is not in that some
        db["whitelist"] = dbs
        if "blacklist" not in db:
            db["blacklist"] = [".travis.yml", ".travis.yaml"]
        load_database(db, client, rc)
    # Chain each collection when it is first asked for rather than now, so a
    # command only reads the collections it actually uses
    client.chained_db = LazyChainedDB(client)
    return client


@contextmanager
def connect(rc, dbs=None):
    """Context manager for ensuring that database is properly setup and
    torn down."""
    client = open_dbs(rc, dbs=dbs)
    yield client
    for db in rc.databases:
        dump_database(db, client, rc)
    client.close()

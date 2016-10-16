"""Helps manage mongodb setup and connections."""
import os
import time
import shutil
import subprocess
from glob import iglob
from warnings import warn
from contextlib import contextmanager

try:
    import hglib
except:
    hglib = None


def load_git_database(db, client, rc):
    """Loads a git database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # get or update the database
    if os.path.isdir(dbdir):
        cmd = ['git', 'pull']
        cwd = dbdir
    else:
        cmd = ['git', 'clone', db['url'], dbdir]
        cwd = None
    subprocess.check_call(cmd, cwd=cwd)
    # import all of the data
    client.load_database(db)

def load_hg_database(db, client, rc):
    """Loads an hg database"""
    if hglib is None:
        raise ImportError('hglib')
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # get or update the database
    if os.path.isdir(dbdir):
        client = hglib.open(dbdir)
        client.pull(update=True, force=True)
    else:
        # Strip off three characters for hg+
        client = hglib.clone(db['url'][3:], dbdir)
    # import all of the data
    client.load_database(db)


def load_database(db, client, rc):
    """Loads a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        load_git_database(db, client, rc)
    elif url.startswith('hg+'):
        load_hg_database(db, client, rc)
    else:
        raise ValueError('Do not know how to load this kind of database')


def dump_git_database(db, client, rc):
    """Dumps a git database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # dump all of the data
    client.dump_database(db)
    # update the repo
    cmd = ['git', 'add'] + to_add
    subprocess.check_call(cmd, cwd=dbdir)
    cmd = ['git', 'commit', '-m', 'regolith auto-commit']
    try:
        subprocess.check_call(cmd, cwd=dbdir)
    except subprocess.CalledProcessError:
        warn('Could not git commit to ' + dbdir, RuntimeWarning)
        return
    cmd = ['git', 'push']
    try:
        subprocess.check_call(cmd, cwd=dbdir)
    except subprocess.CalledProcessError:
        warn('Could not git push from ' + dbdir, RuntimeWarning)
        return


def dump_hg_database(db, client, rc):
    """Dumps an hg database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # dump all of the data
    client.dump_database(db)
    # update the repo
    hgclient = hglib.open(dbdir)
    if len(hgclient.status(include=to_add, modified=True,
                           unknown=True, added=True)) == 0:
        return
    hgclient.commit(message='regolith auto-commit', include=to_add,
                    addremove=True)
    hgclient.push()


def dump_database(db, client, rc):
    """Dumps a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        dump_git_database(db, client, rc)
    elif url.startswith('hg+'):
        dump_hg_database(db, client, rc)
    else:
        raise ValueError('Do not know how to dump this kind of database')


@contextmanager
def connect(rc):
    """Context manager for ensuring that database is properly setup and torn down"""
    client = CLIENTS[rc.client](rc)
    for db in rc.databases:
        load_database(db, client, rc)
    yield client
    for db in rc.databases:
        dump_database(db, client, rc)
    client.close()

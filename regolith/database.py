"""Helps manage mongodb setup and connections."""
import os
import subprocess
from contextlib import contextmanager

from pymongo import MongoClient


def load_git_database(db, rc):
    """Loads a git database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    if os.path.isdir(dbdir):
        cmd = ['git', 'pull']
        cwd = dbdir
    else:
        cmd = ['git', 'clone', db['url'], dbdir]
        cwd = None
    subprocess.check_call(cmd, cwd=cwd)


def load_database(db, rc):
    """Loads a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        load_git_database(db, rc)
    else:
        raise ValueError('Do not know how to load this kind of database')

@contextmanager
def connect(rc):
    proc = subprocess.Popen(['mongod'], universal_newlines=True)
    for db in rc.databases:
        load_database(db, rc)
    client = MongoClient()
    yield client
    proc.terminate()

"""Helps manage mongodb setup and connections."""
import os
import subprocess
from glob import iglob
from contextlib import contextmanager

from pymongo import MongoClient


def load_git_database(db, rc):
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
    dbpath = os.path.join(dbdir, db['path'])
    for f in iglob(os.path.join(dbpath, '*.json')):
        base, ext = os.path.splitext(os.path.split(f)[-1])
        cmd = ['mongoimport', '--db',  db['name'], '--collection', base, '--file', f]
        subprocess.check_call(cmd)


def load_database(db, rc):
    """Loads a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        load_git_database(db, rc)
    else:
        raise ValueError('Do not know how to load this kind of database')


def dump_git_database(db, client, rc):
    """Dumps a git database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # dump all of the data
    dbpath = os.path.join(dbdir, db['path'])
    to_add = []
    for collection in client[db['name']].keys():
        f = os.path.join(dbpath, collection + '.json')
        cmd = ['mongoexport', '--db',  db['name'], '--collection', collection, 
                              '--file', f]
        subprocess.check_call(cmd)
        to_add.append(os.path.join(db['path'], collection + '.json'))
    # update the repo
    cmd = ['git', 'add'] + to_add
    subprocess.check_call(cmd, cwd=dbdir)
    cmd = ['git', 'commit', '-m', 'regolith auto-commit']
    subprocess.check_call(cmd, cwd=dbdir)
    cmd = ['git', 'push']
    subprocess.check_call(cmd, cwd=dbdir)


def dump_database(db, client, rc):
    """Dumps a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        dump_git_database(db, client, rc)
    else:
        raise ValueError('Do not know how to dump this kind of database')

@contextmanager
def connect(rc):
    proc = subprocess.Popen(['mongod'], universal_newlines=True)
    for db in rc.databases:
        load_database(db, rc)
    client = MongoClient()
    yield client
    for db in rc.databases:
        dump_database(db, client, rc)
    proc.terminate()

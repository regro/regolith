"""Helps manage mongodb setup and connections."""
import os
import time
import shutil
import subprocess
from glob import iglob
from warnings import warn
from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ConnectionFailure

from regolith.tools import ON_PYMONGO_V2, ON_PYMONGO_V3

try:
    import hglib
except:
    hglib = None


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

def load_hg_database(db, rc):
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
    elif url.startswith('hg+'):
        load_hg_database(db, rc)
    else:
        raise ValueError('Do not know how to load this kind of database')


def dump_git_database(db, client, rc):
    """Dumps a git database"""
    dbsdir = os.path.join(rc.builddir, '_dbs')
    dbdir = os.path.join(dbsdir, db['name'])
    # dump all of the data
    dbpath = os.path.join(dbdir, db['path'])
    os.makedirs(dbpath, exist_ok=True)
    to_add = []
    colls = client[db['name']].collection_names(include_system_collections=False)
    for collection in colls:
        f = os.path.join(dbpath, collection + '.json')
        cmd = ['mongoexport', '--db',  db['name'], '--collection', collection,
                              '--out', f]
        subprocess.check_call(cmd)
        to_add.append(os.path.join(db['path'], collection + '.json'))
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
    dbpath = os.path.join(dbdir, db['path'])
    os.makedirs(dbpath, exist_ok=True)
    to_add = []
    colls = client[db['name']].collection_names(include_system_collections=False)
    for collection in colls:
        f = os.path.join(dbpath, collection + '.json')
        cmd = ['mongoexport', '--db',  db['name'], '--collection', collection,
                              '--out', f]
        subprocess.check_call(cmd)
        to_add.append(os.path.join(dbdir, db['path'], collection + '.json'))
    # update the repo
    client = hglib.open(dbdir)
    if not any(client.status(include=_)[0][0].decode("ascii") in ('MAR!')
               for _ in to_add):
        return
    client.commit(message='regolith auto-commit', include=to_add,
                  addremove=True)
    client.push()

def dump_database(db, client, rc):
    """Dumps a database"""
    url = db['url']
    if url.startswith('git') or url.endswith('.git'):
        dump_git_database(db, client, rc)
    elif url.startswith('hg+'):
        dump_hg_database(db, client, rc)
    else:
        raise ValueError('Do not know how to dump this kind of database')

def client_is_alive(client):
    """Robust way to check if client is alive"""
    if ON_PYMONGO_V2:
        return client.alive()
    elif ON_PYMONGO_V3:
        cmd = ['mongostat', '--host', 'localhost', '-n', '1']
        try:
            subprocess.check_call(cmd)
            alive = True
        except subprocess.CalledProcessError: 
            alive = False
        return alive
    else:
        raise RuntimeError

def create_client():
    """This creates ensures that a client is connected and alive."""
    client = None
    while client is None:
        try: 
            client = MongoClient()
        except (AutoReconnect, ConnectionFailure):
            time.sleep(0.1)
    while not client_is_alive(client):
        time.sleep(0.1)  # we need tp wait for the server to startup
    return client

@contextmanager
def connect(rc):
    """Context manager for ensuring that database is properly setup and torn down"""
    mongodbpath = rc.mongodbpath
    if os.path.isdir(mongodbpath):
        shutil.rmtree(mongodbpath)
    os.makedirs(mongodbpath)
    proc = subprocess.Popen(['mongod', '--dbpath', mongodbpath], universal_newlines=True)
    print('mongod pid: {0}'.format(proc.pid))
    client = create_client()
    for db in rc.databases:
        load_database(db, rc)
    yield client
    for db in rc.databases:
        dump_database(db, client, rc)
    if ON_PYMONGO_V2:
        client.disconnect()
    elif ON_PYMONGO_V3:
        client.close()
    else:
        raise RuntimeError('did not recognize pymongo version')
    proc.terminate()
    if os.path.isdir(mongodbpath):
        shutil.rmtree(mongodbpath, ignore_errors=True)

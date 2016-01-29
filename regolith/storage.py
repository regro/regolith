"""Tools for document storgage."""
import os
import subprocess


def find_store(rc):
    for store in rc.stores:
        if store['name'] == rc.storename:
            return s
    else:
        msg = "Could not find the store {0!r}".format(rc.storename)
        raise RuntimeError(msg)


def storage_path(store, rc):
    """Computes the storage directory."""
    name, url = store['name'], store['url']
    for db in rc.databases:
        if db['name'] == name and db['url'] == url:
            return os.path.join(rc.builddir, '_dbs', name, store['path'])
    else:
        return os.path.join(rc.builddir, '_stores', name, store['path'])

def sync_git(store, path):
    """Syncs the local documents via git."""
    storedir, _ = os.path.split(path)
    # get or update the storage
    if os.path.isdir(storedir):
        cmd = ['git', 'pull']
        cwd = storedir
    else:
        cmd = ['git', 'clone', store['url'], storedir]
        cwd = None
    subprocess.check_call(cmd, cwd=cwd)


def sync(store, path):
    """Syncs the local documents."""
    url = store['url']
    if url.startswith('git') or url.endswith('.git'):
        sync_git(store, path)
    else:
        raise ValueError('Do not know how to sync this kind of storage.')


def main(rc):
    """Copies files into the local storage location and uploads them."""
    store = find_store(rc)
    path = storage_path(store, rc)
    sync()
    #copy()
    #push()
"""Tools for document storgage."""
import os
import shutil
import subprocess

try:
    import hglib
except:
    hglib = None


def find_store(rc):
    for store in rc.stores:
        if store['name'] == rc.storename:
            return store
    else:
        msg = "Could not find the store {0!r}".format(rc.storename)
        raise RuntimeError(msg)


def storage_path(store, rc):
    """Computes the storage directory."""
    name, url = store['name'], store['url']
    for db in rc.databases:
        if db['name'] == name and db['url'] == url:
            path = os.path.join(rc.builddir, '_dbs', name, store['path'])
            break
    else:
        path = os.path.join(rc.builddir, '_stores', name, store['path'])
    os.makedirs(path, exist_ok=True)
    return path


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


def sync_hg(store, path):
    """Syncs the local documents via hg."""
    storedir, _ = os.path.split(path)
    # get or update the storage
    if os.path.isdir(os.path.join(storedir, ".hg")):
        client = hglib.open(storedir)
        client.pull(update=True, force=True)
    else:
        # Strip off three characters for hg+
        client = hglib.clone(store['url'][3:], storedir)


def sync(store, path):
    """Syncs the local documents."""
    url = store['url']
    if url.startswith('git') or url.endswith('.git'):
        sync_git(store, path)
    elif url.startswith('hg+'):
        sync_hg(store, path)
    else:
        raise ValueError('Do not know how to sync this kind of storage.')


def copydocs(store, path, rc):
    """Copies files to the staging area."""
    for doc in rc.documents:
        dst = os.path.join(path, os.path.split(doc)[1])
        if not rc.force and os.path.isfile(dst):
            raise RuntimeError(dst + ' already exists!')
        shutil.copy2(doc, dst)


def push_git(store, path):
    """Pushes the local documents via git."""
    storedir, _ = os.path.split(path)
    cmd = ['git', 'add', '.']
    subprocess.check_call(cmd, cwd=storedir)
    cmd = ['git', 'commit', '-m', 'regolith auto-store commit']
    try:
        subprocess.check_call(cmd, cwd=storedir)
    except subprocess.CalledProcessError: 
        warn('Could not git commit to ' + storedir, RuntimeWarning)
        return
    cmd = ['git', 'push']
    try:
        subprocess.check_call(cmd, cwd=storedir)
    except subprocess.CalledProcessError: 
        warn('Could not git push from ' + storedir, RuntimeWarning)
        return


def push_hg(store, path):
    """Pushes the local documents via git."""
    storedir, _ = os.path.split(path)
    client = hglib.open(storedir)
    if len(client.status(modified=True, unknown=True, added=True)) == 0:
        return
    client.commit(message='regolith auto-commit', addremove=True)
    client.push()


def push(store, path):
    """Pushes the local documents."""
    url = store['url']
    if url.startswith('git') or url.endswith('.git'):
        push_git(store, path)
    elif url.startswith('hg+'):
        push_hg(store, path)
    else:
        raise ValueError('Do not know how to push to this kind of storage.')


def main(rc):
    """Copies files into the local storage location and uploads them."""
    store = find_store(rc)
    path = storage_path(store, rc)
    sync(store, path)
    copydocs(store, path, rc)
    push(store, path)


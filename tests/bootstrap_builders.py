import json
import os
import shutil
import subprocess
import sys
import tempfile
from copy import deepcopy

from regolith.fsclient import dump_yaml
from regolith.schemas import EXEMPLARS


builder_map = [
    'cv',
    'html',
    'resume',
    'publist',
    'current-pending',
    'preslist'
]


def rmtree(dirname):
    """Remove a directory, even if it has read-only files (Windows).
    Git creates read-only files that must be removed on teardown. See
    https://stackoverflow.com/questions/2656322  for more info.

    Parameters
    ----------
    dirname : str
        Directory to be removed
    """
    try:
        shutil.rmtree(dirname)
    except PermissionError:
        if sys.platform == 'win32':
            subprocess.check_call(['del', '/F/S/Q', dirname], shell=True)
        else:
            raise


def make_db():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = 'regolith_fake'
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(['git', 'init', repo])
    os.chdir(repo)
    with open('README', 'w') as f:
        f.write('testing ' + name)
    with open('regolithrc.json', 'w') as f:
        json.dump({"groupname": "ERGS",
                   "databases": [
                       {"name": "test",
                        'url': repo,
                        "public": True,
                        "path": "db",
                        "local": True}
                   ]}, f)
    os.mkdir('db')
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd['_id']: dd for dd in example}
        else:
            d = {example['_id']: example}
        dump_yaml('db/{}.yaml'.format(coll), d)
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-am', 'Initial readme'])
    yield repo
    os.chdir(cwd)
    rmtree(repo)


def bootstrap_builders():
    g = make_db()
    repo = next(g)
    os.chdir(repo)
    for bm in builder_map:
        if bm == 'html':
            os.makedirs('templates/static')
        subprocess.run(['regolith', 'build', bm, '--no-pdf'], check=True)
        os.chdir(os.path.join(repo, '_build', bm))
        expected_base = os.path.join(os.path.dirname(__file__), 'outputs')
        for root, dirs, files in os.walk('.'):
            for file in files:

                # Use this for bootstrapping the tests,
                # confirm by hand that files look correct
                if root != '.':
                    os.makedirs(os.path.join(expected_base, bm, root),
                                exist_ok=True)
                if root == '.':
                    os.makedirs(os.path.join(expected_base, bm),
                                exist_ok=True)
                    shutil.copyfile(os.path.join(file),
                                    os.path.join(expected_base, bm, file))
                else:
                    shutil.copyfile(os.path.join(root, file),
                                    os.path.join(expected_base, bm, root,
                                                 file))
        os.chdir(repo)
    next(g)


if __name__ == '__main__':
    bootstrap_builders()

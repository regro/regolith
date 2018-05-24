import os
import shutil
import subprocess

from .conftest import make_db
from .test_builders import builder_map


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
                    shutil.copyfile(os.path.join(file),
                                    os.path.join(expected_base, bm, file))
                else:
                    shutil.copyfile(os.path.join(root, file),
                                    os.path.join(expected_base, bm, root,
                                                 file))
    next(g)


if __name__ == '__main__':
    bootstrap_builders()

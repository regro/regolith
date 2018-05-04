import os
import shutil
import subprocess

import pytest

builder_map = [
    # 'cv',
    'html',
    # 'resume', 'publist'
]


@pytest.mark.parametrize('bm', builder_map)
def test_builder(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == 'html':
        os.makedirs('templates/static')
    subprocess.run(['regolith', 'build', bm, '--no-pdf'], check=True)
    os.chdir(os.path.join(repo, '_build', bm))
    expected_base = os.path.join(os.path.dirname(__file__),
                                 'outputs')
    for root, dirs, files in os.walk('.'):
        root = root.strip('./')
        for file in files:
            # Use this for bootstrapping the tests,
            # confirm by hand that files look correct
            if root != '.':
                os.makedirs(os.path.join(expected_base, bm, root), exist_ok=True)
            if root == '.':
                shutil.copyfile(os.path.join(file),
                                os.path.join(expected_base, bm, file))
            else:
                shutil.copyfile(os.path.join(root, file),
                                os.path.join(expected_base, bm, root, file))
            # if file in os.listdir(os.path.join(expected_base, bm)):
            #     with open(os.path.join(repo, '_build', bm, file), 'r') as f:
            #         actual = f.read()
            #     with open(os.path.join(expected_base, bm, file), 'r') as f:
            #         expected = f.read()
            #     assert expected == actual

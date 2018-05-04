import os
import shutil
import subprocess

import pytest


# builder_map = {'builder': [('filename1', 'expected_output')]}
builder_map = ['cv',
               # HTML support pending the group collection
               # 'html',
               'resume', 'publist']

ext_blacklist = ['.pdf']


@pytest.mark.parametrize('bm', builder_map)
def test_builder(bm, make_db):
    repo = make_db
    os.chdir(repo)
    subprocess.run(['regolith', 'build', bm, '--no-pdf'])
    os.chdir(os.path.join(repo, '_build', bm))
    expected_base = os.path.join(os.path.dirname(__file__),
                                 'outputs')
    for root, dirs, files in os.walk('.'):
        for file in files:

            # Use this for bootstrapping the tests,
            # confirm by hand that files look correct
            # os.makedirs(os.path.join(expected_base, bm), exist_ok=True)
            # shutil.copyfile(file, os.path.join(expected_base, bm, file))

            if (file in os.listdir(os.path.join(expected_base, bm))
                    and os.path.splitext(file)[-1] not in ext_blacklist):

                with open(os.path.join(repo, '_build', bm, file), 'r') as f:
                    actual = f.read()
                with open(os.path.join(expected_base, bm, file), 'r') as f:
                    expected = f.read()
                assert expected == actual

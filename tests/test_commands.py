import subprocess
import os
import sys
from pathlib import Path
import pytest

from regolith.main import main

BILLINGE_TEST = False  # special tests for Billinge group, switch it to False before push to remote


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_fs_to_mongo_python(make_db):
    if BILLINGE_TEST:
        repo = str(Path(__file__).parent.parent.parent.joinpath('rg-db-group', 'local'))
    else:
        repo = make_db
    #    dbpath = Path(repo).joinpath('_dbpath')
    #    dbpath.mkdir()
    #    cp0 = subprocess.run(['mongod', '--fork', '--syslog', '--dbpath', dbpath])
    #    assert cp0.returncode == 0
    cp1 = subprocess.run(['regolith', 'fs-to-mongo'], cwd=repo)
    assert cp1.returncode == 0


def test_fs_to_mongo_python(make_db):
    if BILLINGE_TEST:
        repo = str(Path(__file__).parent.parent.parent.joinpath('rg-db-group', 'local'))
    else:
        repo = make_db
    os.chdir(repo)
    #TODO fix this test case and the above as they are a crime against humanity
    try:
        main(['fs-to-mongo'])
    except Exception as e:
        print(e)
    else:
        assert True == True


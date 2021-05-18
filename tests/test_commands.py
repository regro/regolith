import subprocess
from pathlib import Path

BILLINGE_TEST = False  # special tests for Billinge group, switch it to False before push to remote


def test_fs_to_mongo(make_db):
    if BILLINGE_TEST:
        repo = str(Path(__file__).parent.parent.parent.joinpath('rg-db-group', 'local'))
    else:
        repo = make_db
    #    dbpath = Path(repo).joinpath('_dbpath')
    #    dbpath.mkdir()
    #    cp0 = subprocess.run(['mongod', '--fork', '--syslog', '--dbpath', dbpath])
    #    assert cp0.returncode == 0
    cp1 = subprocess.run(['regolith', 'fs-to-mongo'], cwd=repo, shell=True)
    assert cp1.returncode == 0

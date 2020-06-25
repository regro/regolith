import subprocess

BILLINGE_TEST = False  # special tests for Billinge group, switch it to False before push to remote


def test_fs_to_mongo(make_db):
    if BILLINGE_TEST:
        from pathlib import Path
        repo = str(Path(__file__).parent.parent.parent.joinpath('rg-db-group', 'local'))
    else:
        repo = make_db
    cp0 = subprocess.run(['mongod'])
    if cp0.returncode != 0:
        print("Server failed to start.")
        return
    cp1 = subprocess.run(['regolith', 'fs-to-mongo'], cwd=repo)
    assert cp1.returncode == 0

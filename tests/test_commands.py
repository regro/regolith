import subprocess

BILLINGE_TEST = False  # special tests for Billinge group, switch it to False before push to remote


def test_fs_to_mongo(make_db):
    if BILLINGE_TEST:
        from pathlib import Path
        repo = str(Path(__file__).parent.parent.parent.joinpath('rg-db-group', 'local'))
    else:
        repo = make_db
    cp = subprocess.run(['regolith', 'fs-to-mongo'], cwd=repo)
    assert cp.returncode == 0

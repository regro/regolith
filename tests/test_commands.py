import subprocess


def test_fs_to_mongo(make_db):
    repo = make_db
    cp = subprocess.run(['regolith', 'fs-to-mongo'], cwd=repo)
    assert cp.returncode == 0

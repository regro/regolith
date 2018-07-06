import os
import subprocess
from regolith.storage import find_store, storage_path


def test_cmd(make_db, tmpdir):
    repo = make_db
    os.chdir(repo)
    subprocess.check_call(['touch', 'myfile.tex'], cwd=tmpdir)
    subprocess.check_call(['regolith', 'store', 'myfile.tex'], cwd=tmpdir)
    assert 'myfile.tex' in os.listdir(storage_path(find_store())
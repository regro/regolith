import os
import subprocess
from regolith.storage import find_store, storage_path
from regolith.runcontrol import load_rcfile, DEFAULT_RC


def test_cmd(make_db, tmpdir):
    repo = make_db
    os.chdir(repo)
    subprocess.check_call(['touch', 'myfile2.tex'], cwd=tmpdir)
    subprocess.check_call(['regolith', 'store', 'store',
                           os.path.join(tmpdir, 'myfile2.tex')])
    rc = DEFAULT_RC
    rc._update(load_rcfile('regolithrc.json'))
    assert 'myfile.tex' in os.listdir(storage_path(find_store(rc), rc))

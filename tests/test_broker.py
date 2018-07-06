import os
import subprocess

from regolith.broker import Broker, load_db


def test_round_trip(make_db, tmpdir):
    repo = make_db
    os.chdir(repo)
    subprocess.check_call(['touch', 'myfile.tex'], cwd=tmpdir)
    db = load_db()
    db.add_file(db['projects']['Cyclus'], 'myfile',
                os.path.join(tmpdir, 'myfile.tex'))
    ret = db.get_file(db['projects']['Cyclus'], 'myfile')
    assert ret == '/tmp/regolith_fake/myfile.tex'

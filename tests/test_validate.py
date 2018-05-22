import os
import subprocess


def test_validate(make_db):
    repo = make_db
    os.chdir(repo)
    out = subprocess.check_output(['regolith', 'validate']).decode('utf-8')
    assert 'NO ERRORS IN DBS' in out


def test_validate_bad(make_bad_db):
    repo = make_bad_db
    os.chdir(repo)
    out = subprocess.check_output(['regolith', 'validate']).decode('utf-8')
    assert 'Errors found in ' in out
    assert 'NO ERRORS IN DBS' not in out

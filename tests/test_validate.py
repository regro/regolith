import os
from io import StringIO
import subprocess
import sys

import pytest

from regolith.main import main


def test_validate_python(make_db):
    repo = make_db
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    main(['validate'])
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert 'NO ERRORS IN DBS' in out


def test_validate_bad_python(make_bad_db):
    repo = make_bad_db
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    main(['validate'])
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert 'Errors found in ' in out
    assert 'NO ERRORS IN DBS' not in out


@pytest.mark.skipif(os.name == 'nt',
                    reason="Windows not working with subprocess run")
def test_validate(make_db):
    repo = make_db
    os.chdir(repo)
    out = subprocess.check_output(['regolith', 'validate']).decode('utf-8')
    assert 'NO ERRORS IN DBS' in out


@pytest.mark.skipif(os.name == 'nt',
                    reason="Windows not working with subprocess run")
def test_validate_bad(make_bad_db):
    repo = make_bad_db
    os.chdir(repo)
    out = subprocess.check_output(['regolith', 'validate']).decode('utf-8')
    assert 'Errors found in ' in out
    assert 'NO ERRORS IN DBS' not in out

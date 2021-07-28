import os
import sys
from io import StringIO

import pytest
from xonsh.lib import subprocess as sp

from regolith.main import main


def test_validate_python(make_db):
    repo = make_db
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    main(["validate"])
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert "NO ERRORS IN DBS" in out


def test_validate_python_single_col(make_db):
    repo = make_db
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    main(["validate", "--collection", "projecta"])
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert "NO ERRORS IN DBS" in out


def test_validate_bad_python(make_bad_db):
    repo = make_bad_db
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    with pytest.raises(SystemExit):
        main(["validate"])
    out = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert "Errors found in " in out
    assert "NO ERRORS IN DBS" not in out

@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_validate(make_db):
    repo = make_db
    os.chdir(repo)
    out = sp.run(["regolith", "validate"], check=False).out
    assert "NO ERRORS IN DBS" in out

@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_validate_bad(make_bad_db):
    repo = make_bad_db
    os.chdir(repo)
    out = sp.run(["regolith", "validate"], check=False).out
    assert "Errors found in " in out
    assert "NO ERRORS IN DBS" not in out

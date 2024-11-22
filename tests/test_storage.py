import copy
import os
import subprocess
import sys

import pytest

from regolith.runcontrol import DEFAULT_RC, load_rcfile
from regolith.storage import find_store, storage_path


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_cmd(make_db, tmpdir):
    repo = make_db
    os.chdir(repo)
    subprocess.check_call(["touch", "myfile2.tex"], cwd=tmpdir)
    subprocess.check_call(["regolith", "store", "store", os.path.join(tmpdir, "myfile2.tex")])
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    assert "myfile.tex" in os.listdir(storage_path(find_store(rc), rc))

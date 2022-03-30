import json
import os
import sys
from io import StringIO

from regolith.main import main
from regolith.runcontrol import DEFAULT_RC

from regolith import __version__

def test_version():
    sys.stdout = StringIO()
    main(["--version"])
    assert sys.stdout.getvalue() == "{}\n".format(__version__)

def test_user_rc(make_db):
    repo = make_db
    DEFAULT_RC.user_config = os.path.join(repo, "user.json")
    os.chdir(repo)
    backup = sys.stdout
    sys.stdout = StringIO()
    main(["rc"])
    out1 = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup

    with open(DEFAULT_RC.user_config, "w") as f:
        json.dump({"hello": "world"}, f)

    backup = sys.stdout
    sys.stdout = StringIO()
    main(["rc"])
    out2 = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    assert out1 != out2
    assert "hello" in out2

import json
import os
import subprocess
import sys
from io import StringIO

import pytest

from regolith import __version__
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC


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


@pytest.mark.parametrize(
    "module",
    [
        # Test that starting up imports none of the heavy libraries.  Only the
        # target a command was asked for should pull its dependencies in, so
        # that a command which touches no builder pays for none of them.
        # C1: pandas, reached from the beamplan builder
        "pandas",
        # C2: matplotlib, reached from the attestations helper
        "matplotlib",
        # C3: pypdf, reached from the meals log builder
        "pypdf",
        # C4: habanero and the google api client, reached from regolith.tools
        "habanero",
        "googleapiclient",
    ],
)
def test_startup_imports_nothing_heavy(module):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import regolith.main, sys; sys.exit(1 if '{module}' in sys.modules else 0)",
        ],
        capture_output=True,
    )
    assert result.returncode == 0, f"{module} is imported just to start regolith"


def test_naming_a_builder_does_not_import_it():
    # Test that the registry can list the valid targets without importing
    # them, since the command line names them in its help text.  Run in a
    # subprocess because another test in this session may already have
    # imported the builder.
    check = (
        "import sys\n"
        "from regolith.builder import BUILDERS\n"
        "assert 'cv' in BUILDERS\n"
        "assert 'not-a-builder' not in BUILDERS\n"
        "assert sys.modules.get('regolith.builders.cvbuilder') is None, 'named it and imported it'\n"
        "assert BUILDERS['cv'].__name__ == 'CVBuilder'\n"
    )
    result = subprocess.run([sys.executable, "-c", check], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

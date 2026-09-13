"""Tests for the commands regolith installs.

The scripts are plain files listed in ``script-files``, installed by
setuptools without being looked at, so nothing here is checked at build
time: a script that names a module that does not exist installs just as
happily as one that works.  These look at them instead.
"""

import pathlib
import re
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTED = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["setuptools"]["script-files"]
RUNS_MODULE = re.compile(r"-m\s+(?P<module>[\w.]+)")


def test_every_script_the_package_installs_is_there():
    # Test that script-files names files that exist.  A script renamed on one
    # line and not the other goes missing from the install rather than
    # failing the build
    assert [name for name in LISTED if not (ROOT / name).is_file()] == []


@pytest.mark.parametrize("bat", sorted(p.name for p in (ROOT / "scripts").glob("*.bat")))
def test_a_windows_launcher_runs_a_module_that_is_there(bat):
    # Test that each .bat starts something.  Every one of them ran "python -m"
    # against its own file name -- "-m helper_gui", "-m regolith" -- and none
    # of those was an importable module, so none of the Windows launchers
    # could start anything.  They fail where nobody who works on regolith
    # would see it
    import importlib.util

    text = (ROOT / "scripts" / bat).read_text()
    for module in RUNS_MODULE.findall(text):
        assert importlib.util.find_spec(module) is not None, f"{bat} runs -m {module}, which is not a module"


@pytest.mark.parametrize("script", sorted(name for name in LISTED if not name.endswith(".bat")))
def test_a_script_that_calls_main_imports_one(script):
    # Test the thing every one of these scripts does: call main().  Both
    # profile scripts called it without importing one, so neither had ever
    # run, and nothing said so until somebody tried to profile something
    text = (ROOT / script).read_text()
    if "main()" not in text:
        return
    assert re.search(r"^from [\w.]+ import .*\bmain\b", text, re.MULTILINE), f"{script} calls main() without one"

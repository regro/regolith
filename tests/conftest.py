"""Copyright (c) 2017, Anthony Scopatz
All rights reserved."""
import json
import os
import shutil
from xonsh.lib import subprocess
import sys
import tempfile
from copy import deepcopy

import pytest

from regolith.fsclient import dump_yaml
from regolith.schemas import EXEMPLARS


@pytest.fixture(scope="session")
def make_db():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "regolith_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                    }
                ],
                "stores": [
                    {
                        "name": "store",
                        "url": repo,
                        "path": repo,
                        "public": True,
                    }
                ],
                # 'storename': 'store',
            },
            f,
        )
    os.mkdir("db")
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        dump_yaml("db/{}.yaml".format(coll), d)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-am", "Initial readme"])
    yield repo
    os.chdir(cwd)
    rmtree(repo)


@pytest.fixture(scope="session")
def make_bad_db():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "regolith_fake_bad"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                    }
                ],
            },
            f,
        )
    os.mkdir("db")
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        d.update({"bad": {"_id": "bad", "bad": True}})
        if coll == "presentations":
            d.update(
                {
                    "bad_inst": {
                        "_id": "bad_inst",
                        "institution": "noinstitution",
                        "department": "nodept",
                    }
                }
            )
        dump_yaml("db/{}.yaml".format(coll), d)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-am", "Initial readme"])
    yield repo
    os.chdir(cwd)
    rmtree(repo)


def rmtree(dirname):
    """Remove a directory, even if it has read-only files (Windows).
    Git creates read-only files that must be removed on teardown. See
    https://stackoverflow.com/questions/2656322  for more info.

    Parameters
    ----------
    dirname : str
        Directory to be removed
    """
    try:
        shutil.rmtree(dirname)
    except PermissionError:
        if sys.platform == "win32":
            subprocess.check_call(["del", "/F/S/Q", dirname], shell=True)
        else:
            raise

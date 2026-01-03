import json
import os
import shutil
import sys
import tempfile
from copy import deepcopy

from xonsh.api import subprocess

from regolith.broker import load_db
from regolith.fsclient import dump_yaml
from regolith.main import main
from regolith.schemas import EXEMPLARS

builder_map = [
    "cv",
    "html",
    "resume",
    "publist",
    "current-pending",
    "preslist",
    "figure",
    "reimb",
]


def prep_figure():
    # Make latex file with some jinja2 in it
    text = r"""
    \include{ {{-get_file_path(db['groups']['ergs'], 'hello')-}}}"""
    with open("figure.tex", "w") as f:
        f.write(text)
    # make file to be loaded
    os.makedirs("fig", exist_ok=True)
    with open("fig/hello.txt", "w") as f:
        f.write("hello world")
    # load the db and register the file
    db = load_db()
    print(db.get_file_path(db["groups"]["ergs"], "hello"))
    if not db.get_file_path(db["groups"]["ergs"], "hello"):
        db.add_file(db["groups"]["ergs"], "hello", "fig/hello.txt")


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


def make_db():
    """A test fixutre that creates and destroys a git repo in a
    temporary directory.

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
                "force": False,
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


expected_base = os.path.join(os.path.abspath(os.path.dirname(__file__)), "outputs")


def bootstrap_builders():
    g = make_db()
    repo = next(g)
    os.chdir(repo)
    for bm in builder_map:
        if bm == "html":
            os.makedirs("templates/static")
        if bm == "figure":
            prep_figure()
        main(["build", bm, "--no-pdf"])
        os.chdir(os.path.join(repo, "_build", bm))
        os.makedirs(expected_base, exist_ok=True)
        for root, dirs, files in os.walk("."):
            for file in files:
                # Use this for bootstrapping the tests,
                # confirm by hand that files look correct
                if root == ".":
                    os.makedirs(os.path.join(expected_base, bm), exist_ok=True)
                    shutil.copyfile(
                        os.path.join(file),
                        os.path.join(expected_base, bm, file),
                    )
                else:
                    os.makedirs(os.path.join(expected_base, bm, root), exist_ok=True)
                    shutil.copyfile(
                        os.path.join(root, file),
                        os.path.join(expected_base, bm, root, file),
                    )
        os.chdir(repo)
    next(g)


if __name__ == "__main__":
    bootstrap_builders()

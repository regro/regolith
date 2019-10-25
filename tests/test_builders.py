import os
import shutil
from xonsh.lib import subprocess

import pytest

from regolith.broker import load_db
from regolith.main import main

import openpyxl

builder_map = [
    "cv",
    "html",
    "resume",
    "publist",
    "current-pending",
    "preslist",
    "reimb",
    "figure",
    "review-man",
]

xls_check = ("B17", "B20", "B36")


def prep_figure():
    # Make latex file with some jinja2 in it
    text = r"""
    \include{ {{-get_file(db['groups']['ergs'], 'hello')-}}}"""
    with open("figure.tex", "w") as f:
        f.write(text)
    # make file to be loaded
    os.makedirs("fig", exist_ok=True)
    with open("fig/hello.txt", "w") as f:
        f.write("hello world")
    # load the db and register the file
    db = load_db()
    print(db.get_file(db["groups"]["ergs"], "hello"))
    if not db.get_file(db["groups"]["ergs"], "hello"):
        db.add_file(db["groups"]["ergs"], "hello", "fig/hello.txt")


@pytest.mark.parametrize("bm", builder_map)
def test_builder(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == "figure":
        prep_figure()
    if bm == "html":
        os.makedirs("templates/static", exist_ok=True)
    subprocess.run(["regolith", "build", bm, "--no-pdf"], check=True, cwd=repo)
    os.chdir(os.path.join(repo, "_build", bm))
    expected_base = os.path.join(os.path.dirname(__file__), "outputs")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(os.path.join(expected_base, bm, root)):
                fn1 = os.path.join(repo, "_build", bm, root, file)
                if bm == "reimb":
                    actual = openpyxl.load_workbook(fn1)["T&B"]
                    actual = [str(actual[b]) for b in xls_check]
                else:
                    with open(fn1, "r") as f:
                        actual = f.read()
                fn2 = os.path.join(expected_base, bm, root, file)
                if bm == "reimb":
                    expected = openpyxl.load_workbook(fn2)["T&B"]
                    expected = [str(expected[b]) for b in xls_check]
                else:
                    with open(fn2, "r") as f:
                        expected = f.read()

                # Skip because of a date time in
                if file != "rss.xml":
                    # Fixme proper fix for testing hard coded filepaths on windows
                    if os.name == "nt":
                        if "tmp" not in expected:
                            if "../.." not in expected:
                                assert expected == actual
                    else:
                        assert expected == actual


@pytest.mark.parametrize("bm", builder_map)
def test_builder_python(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == "figure":
        prep_figure()
    if bm == "html":
        os.makedirs("templates/static", exist_ok=True)
    main(["build", bm, "--no-pdf"])
    os.chdir(os.path.join(repo, "_build", bm))
    expected_base = os.path.join(os.path.dirname(__file__), "outputs")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(os.path.join(expected_base, bm, root)):
                fn1 = os.path.join(repo, "_build", bm, root, file)
                if bm == "reimb":
                    actual = openpyxl.load_workbook(fn1)["T&B"]
                    actual = [str(actual[b]) for b in xls_check]
                else:
                    with open(fn1, "r") as f:
                        actual = f.read()
                fn2 = os.path.join(expected_base, bm, root, file)
                if bm == "reimb":
                    expected = openpyxl.load_workbook(fn2)["T&B"]
                    expected = [str(expected[b]) for b in xls_check]
                else:
                    with open(fn2, "r") as f:
                        expected = f.read()

                # Skip because of a date time in
                if file != "rss.xml":
                    # Fixme proper fix for testing hard coded filepaths on windows
                    if os.name == "nt":
                        if "tmp" not in expected:
                            if "../.." not in expected:
                                assert expected == actual
                    else:
                        assert expected == actual

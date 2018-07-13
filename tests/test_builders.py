import os
import shutil
from xonsh.lib import subprocess

import pytest

from regolith.main import main

builder_map = [
    "cv",
    "html",
    "resume",
    "publist",
    "current-pending",
    "preslist",
]


@pytest.mark.parametrize("bm", builder_map)
def test_builder(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == "html":
        os.makedirs("templates/static", exist_ok=True)
    subprocess.run(["regolith", "build", bm, "--no-pdf"], check=True,
                   cwd=repo)
    os.chdir(os.path.join(repo, "_build", bm))
    expected_base = os.path.join(os.path.dirname(__file__), "outputs")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(os.path.join(expected_base, bm, root)):
                with open(
                    os.path.join(repo, "_build", bm, root, file), "r"
                ) as f:
                    actual = f.read()

                with open(
                    os.path.join(expected_base, bm, root, file), "r"
                ) as f:
                    expected = f.read()

                # Skip because of a date time in
                if file != "rss.xml":
                    assert expected == actual


@pytest.mark.parametrize("bm", builder_map)
def test_builder_python(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == "html":
        os.makedirs("templates/static", exist_ok=True)
    main(["build", bm, "--no-pdf"])
    os.chdir(os.path.join(repo, "_build", bm))
    expected_base = os.path.join(os.path.dirname(__file__), "outputs")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(os.path.join(expected_base, bm, root)):
                with open(
                    os.path.join(repo, "_build", bm, root, file), "r"
                ) as f:
                    actual = f.read()

                with open(
                    os.path.join(expected_base, bm, root, file), "r"
                ) as f:
                    expected = f.read()

                # Skip because of a date time in
                if file != "rss.xml":
                    assert expected == actual


@pytest.mark.parametrize('bm', builder_map)
def test_builder_python(bm, make_db):
    repo = make_db
    os.chdir(repo)
    if bm == 'html':
        os.makedirs('templates/static', exist_ok=True)
    main(['build', bm, '--no-pdf'])
    os.chdir(os.path.join(repo, '_build', bm))
    expected_base = os.path.join(os.path.dirname(__file__),
                                 'outputs')
    for root, dirs, files in os.walk('.'):
        for file in files:

            # Use this for bootstrapping the tests,
            # confirm by hand that files look correct
            # if root != '.':
            #     os.makedirs(os.path.join(expected_base, bm, root),
            #                 exist_ok=True)
            # if root == '.':
            #     shutil.copyfile(os.path.join(file),
            #                     os.path.join(expected_base, bm, file))
            # else:
            #     shutil.copyfile(os.path.join(root, file),
            #                     os.path.join(expected_base, bm, root, file))

            if file in os.listdir(os.path.join(expected_base, bm, root)):
                with open(os.path.join(repo, '_build', bm, root, file),
                          'r') as f:
                    actual = f.read()

                with open(os.path.join(expected_base, bm, root, file),
                          'r') as f:
                    expected = f.read()

            # Skip because of a date time in
                if file != 'rss.xml':
                    assert expected == actual

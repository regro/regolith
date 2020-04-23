import os
import shutil
from xonsh.lib import subprocess
import sys

import pytest

from regolith.broker import load_db
from regolith.main import main

import openpyxl

helper_map = [
    (["helper", "hello", "--person", "Simon"], "hello Simon\n"),
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre","-s", "downloaded", "-t", "A flat world theory"],
      "A. Einstein proposal has been added/updated in proposal reviews\n"),
    #(["a_manrev", "Einstein", "Nature", "2020-04-11"],
     #"refereeReports")
]


@pytest.mark.parametrize("hm", helper_map)
def test_helper_python(hm, make_db, capsys):
    repo = make_db
    os.chdir(repo)
    main(args=hm[0])
    out, err = capsys.readouterr()
    assert out == hm[1]
    output = False
    if os.path.isdir(os.path.join(repo, "_build", hm[0][1])):
        output = True
        os.chdir(os.path.join(repo, "_build", hm[0][1]))
    expected_base = os.path.join(os.path.dirname(__file__), "outputs")
    for root, dirs, files in os.walk("."):
        for file in files:
            if output:
                if file in os.listdir(os.path.join(expected_base, hm[0][1], root)):
                    fn1 = os.path.join(repo, "_build", hm[0][1], root, file)
                    with open(fn1, "r") as f:
                        actual = f.read()
                    fn2 = os.path.join(expected_base, hm[0][1], root, file)
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

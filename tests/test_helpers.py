import os
from pathlib import Path
import pytest

from regolith.main import main


helper_map = [
    (["helper", "hello", "--person", "Simon"], "hello Simon\n"),
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre","-s", "downloaded", "-t", "A flat world theory"],
      "A. Einstein proposal has been added/updated in proposal reviews\n"),
    (["helper", "a_grppub_readlist", "test the lister",
      "A list to test the lister", "pdf", "--purpose", "Test the lister"],
     "test_the_lister has been added in reading_lists\n"),
    (["helper", "a_projectum", "New projectum", "lyang",
      "--date", "2020-04-29", "-c", "afriend", "-d", "more work",
      "-m", "ascopatz", "-g", "SymPy-1.1"],
     "20ly_newprojectum has been added in projecta\n"),
    (["helper", "l_milestones", "--verbose"],
     "2020-05-06: lead: lyang, 20ly_newprojectum, status: planned\n    Title: Kick off meeting\n    Purpose: roll out of project to team\n    Audience: ['pi', 'lead', 'group members', 'collaborators']\n2020-05-06: lead: ascopatz, 20sb_firstprojectum, status: planned\n    Title: Kick off meeting\n    Purpose: roll out of project to team\n    Audience: ['pi', 'lead', 'group members', 'collaborators']\n2020-05-20: lead: lyang, 20ly_newprojectum, status: planned\n    Title: Project lead presentation\n    Purpose: lead presents background reading and initial project plan\n    Audience: ['pi', 'lead', 'group members']\n2020-05-20: lead: ascopatz, 20sb_firstprojectum, status: planned\n    Title: Project lead presentation\n    Purpose: lead presents background reading and initial project plan\n    Audience: ['pi', 'lead', 'group members']\n2020-05-27: lead: lyang, 20ly_newprojectum, status: planned\n    Title: planning meeting\n    Purpose: develop a detailed plan with dates\n    Audience: ['pi', 'lead', 'group members']\n2020-05-27: lead: ascopatz, 20sb_firstprojectum, status: planned\n    Title: planning meeting\n    Purpose: develop a detailed plan with dates\n    Audience: ['pi', 'lead', 'group members']\n"
     ),
    (["helper", "l_milestones", "--verbose", "-l", "lyang"],
     "2020-05-06: lead: lyang, 20ly_newprojectum, status: planned\n    Title: Kick off meeting\n    Purpose: roll out of project to team\n    Audience: ['pi', 'lead', 'group members', 'collaborators']\n2020-05-20: lead: lyang, 20ly_newprojectum, status: planned\n    Title: Project lead presentation\n    Purpose: lead presents background reading and initial project plan\n    Audience: ['pi', 'lead', 'group members']\n2020-05-27: lead: lyang, 20ly_newprojectum, status: planned\n    Title: planning meeting\n    Purpose: develop a detailed plan with dates\n    Audience: ['pi', 'lead', 'group members']\n"
     ),
]


@pytest.mark.parametrize("hm", helper_map)
def test_helper_python(hm, make_db, capsys):
    repo = Path(make_db)
    testfile = Path(__file__)
    os.chdir(repo)

    main(args=hm[0])
    out, err = capsys.readouterr()
    assert out == hm[1]

    builddir = repo / "_build" / hm[0][1]
    expecteddir = testfile.parent / "outputs" / hm[0][1]
    are_outfiles = any(builddir.iterdir())
    if are_outfiles and not expecteddir.is_dir():
        print("WARNING: there are built outputs that are not being tested")
    if are_outfiles and expecteddir.is_dir():
        assert_outputs(builddir,expecteddir)

    builddir = repo / "db"
    if expecteddir.is_dir():
        assert_outputs(builddir,expecteddir)


def assert_outputs(builddir,expecteddir):
    """

    Parameters
    ----------
    builddir pathlib.Path object
      the directory where the helper has built the output
    expecteddir pathlib.Path object
      the directory where the expected output is found
    """
    os.chdir(builddir)
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(expecteddir / root):
                fn1 = builddir / root / file
                with fn1.open(mode="r") as f:
                    actual = f.read()
                fn2 = expecteddir / root / file
                with fn2.open(mode="r") as f:
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


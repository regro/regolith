import os
from pathlib import Path
import pytest

from regolith.main import main

helper_map = [
    (["helper", "hello", "--person", "Simon"], "hello Simon\n"),
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre", "-s", "downloaded", "-t", "A flat world theory"],
     "A. Einstein proposal has been added/updated in proposal reviews\n"),
    (["helper", "a_grppub_readlist", "test the lister",
      "A list to test the lister", "pdf", "--purpose", "Test the lister"],
     "test_the_lister has been added in reading_lists\n"),
    (["helper", "a_projectum", "New projectum", "lyang",
      "--date", "2020-04-29", "-c", "afriend", "-d", "more work",
      "-m", "ascopatz", "-g", "SymPy-1.1", "-u", "2021-01-01"],
     "20ly_newprojectum has been added in projecta\n"),
    (["helper", "a_proposal", "a new proposal", "100.0", "To destroy numbers",
      "--begin_date", "2020-09-15", "--end_date", "2022-02-14", "--duration", "16.89",
      "-a", "Kurt Godel", "MC Escher", "Johann Sebastian Bach", "-c", "Bitcoin",
      "--other_agencies", "Flatland", "-n", "this is a sample added proposal"],
     "20_anewproposal has been added in proposals\n"),
    (["helper", "a_todo", "test, due date is 4 days from the begin date", "4", "-i", "jwzang", "-b", "2020-06-24"],
     "The task has been added in todolist.\n"),
    (["helper", "l_milestones", "--verbose"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_milestones", "--verbose", "-l", "lyang"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_projecta", "--verbose"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose", "-l", "ascopatz"],
     "20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose", "-p", "ascopatz"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--grant", "SymPy-1.1"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--ended", "-d", "2020-06-02"],
     "20sb_firstprojectum    My first projectum\n    Lead: ascopatz    Members: ascopatz    Collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_grants", "-c", "-d", "2020-05-25"],
     "sym2.0, awardnr: , acctn: , 2019-06-01 to 2030-12-31\n, awardnr: , acctn: GG012345, 2015-10-01 to 2025-09-30\n"
     ),
    (["helper", "l_members", "-v"],
     "Simon J. L. Billinge, professor | group_id: sbillinge\n"
     "    orcid: 0000-0002-9432-4248 | github_id: None\n"
     "Anthony Scopatz, professor | group_id: scopatz\n"
     "    orcid: 0000-0002-9432-4248 | github_id: ascopatz\n"
     ),
    (["helper", "l_members", "-f", "name", "sco"],
     "scopatz    \n"
     ),
    (["helper", "l_contacts", "run", "-n", "ny", "-i", "col", "-o", "coffee", "-d", "2020-01-15", "-r", "2"],
     "name: Anthony B Friend, institution: columbiau, email: friend@deed.com\n"
     ),
    (["helper", "l_contacts", "run", "-n", "ny", "-i", "col", "-o", "coffee", "-d", "2019-01-15", "-r", "2"],
     ""
     ),
    (["helper", "u_milestone", "20sb_firstprojectum", "--index", "4",
      "-s", "p","-t", "m", "--due_date", "2020-05-30"],
     "20sb_firstprojectum has been updated in projecta\n"
     ),
    (["helper", "u_milestone", "20sb_firstprojectum", "-v"],
     "Please choose from one of the following to update/add:\n"
     "1. new milestone\n"
     "2. kickoff    due date: 2020-05-06:\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     status: finished\n"
     "3. Project lead presentation    due date: 2020-05-20:\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objetive: lead presents background reading and initial project plan\n"
     "     status: proposed\n"
     "     type: meeting\n"
     "4. planning meeting    due date: 2020-05-30:\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objetive: develop a detailed plan with dates\n"
     "     status: proposed\n"
     "     type: meeting\n"
     "5. deliverable    due date: 2021-05-05:\n"
     "     audience: ['beginning grad in chemistry']\n"
     "     status: finalized\n"
     ),
    (["helper", "u_logurl", "20sb", "-n", "1", "https://docs.google.com/document/d/1pQMFpuI"],
     "20sb_firstprojectum has been updated with a log_url of https://docs.google.com/document/d/1pQMFpuI\n"
     ),
    (["helper", "u_logurl", "20ly", "https://docs.google.com/document/d/1pQMFpuI"],
     "There does not seem to be a projectum with this exact name in this database.\n"
     "However, there are projecta with similar names: \n"
     "1. 20ly_newprojectum     current url: \n"
     "Please rerun the u_logurl helper with the same name as previously inputted, "
     "but with the addition of -n followed by a number corresponding to one of the "
     "above listed projectum ids that you would like to update.\n"
     ),
    (["helper", "u_contact", "afriend", "--index", "2",
      "--notes", "Test note", "-a", "Friend", "--date", "2020-01-02"],
     "afriend has been added/updated in contacts\n"
     ),
    (["helper", "u_contact", "Anthony", "--date", "2020-01-02"],
     "Please rerun the helper specifying '-n list-index' to update item number 'list-index':\n"
     "1. Anthony as a new contact\n"
     "2. Anthony B Friend    id: afriend\n"
     ),
    (["helper", "u_contact", "Maria", "--date", "2020-01-02"],
     "Please rerun the helper specifying '-n list-index' to update item number 'list-index':\n"
     "1. Maria as a new contact\n"
     ),
    (["helper", "l_todo", "-i", "jwzang", "-f", "Jiawei", "-d", "30"],
     "1. prepare the presentation\n"
     ),
    (["helper", "l_todo", "-i", "jwzang", "-f", "Jiawei"],
     "1. Jiawei: test\n2. Everyone: Clear out-of-date prums milestones.\n3. test, due date is 4 days from the begin date\n4. read paper\n5. prepare the presentation\n"
     ),
    (["helper", "l_todo", "-i", "ascopatz", "-f", "asc"],
     "1. 20sb_firstprojectum, Project lead presentation\n2. 20sb_firstprojectum, planning meeting\n3. Everyone: Clear out-of-date prums milestones.\n4. 20sb_firstprojectum, deliverable\n"
     ),
    (["helper", "l_todo","-v", "-i", "jwzang", "-f", "Jiawei"],
     "1. Jiawei: test\n     --(no mark, due: 2020-06-18, None min, importance:1, start date: None)\n2. Everyone: Clear out-of-date prums milestones.\n     --(no mark, due: 2020-06-18, None min, importance:1, start date: None)\n3. test, due date is 4 days from the begin date\n     --(2, due: 2020-06-28, 60.0 min, importance:1, start date: 2020-06-24)\n4. read paper\n     --(0, due: 2020-07-19, 60.0 min, importance:2, start date: 2020-06-15)\n5. prepare the presentation\n     --(1, due: 2020-07-29, 30.0 min, importance:0, start date: 2020-06-22)\n"
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
        assert_outputs(builddir, expecteddir)

    builddir = repo / "db"
    if expecteddir.is_dir():
        assert_outputs(builddir, expecteddir)


def assert_outputs(builddir, expecteddir):
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
                    # Fixme proper fix for testing hard coded filepaths on
                    # windows
                    if os.name == "nt":
                        if "tmp" not in expected:
                            if "../.." not in expected:
                                assert expected == actual
                    else:
                        assert expected == actual

import os
from pathlib import Path
import pytest

from regolith.main import main

helper_map = [
    (["helper", "hello", "--person", "Simon"], "hello Simon\n"),
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre", "--status", "downloaded", "--title", "A flat world theory"],
     "A. Einstein proposal has been added/updated in proposal reviews\n"),
    (["helper", "a_grppub_readlist", "test the lister",
      "A list to test the lister", "pdf", "--purpose", "Test the lister"],
     "test_the_lister has been added in reading_lists\n"),
    (["helper", "a_projectum", "New projectum", "lyang",
      "--date", "2020-04-29", "--collaborators", "afriend", "--description", "more work",
      "--group_members", "ascopatz", "--grants", "SymPy-1.1", "--due_date", "2021-01-01"],
     "20ly_newprojectum has been added in projecta\n"),
    (["helper", "a_proposal", "a new proposal", "100.0", "To destroy numbers",
      "--begin_date", "2020-09-15", "--end_date", "2022-02-14", "--duration", "16.89",
      "--authors", "Kurt Godel", "MC Escher", "Johann Sebastian Bach", "--currency", "Bitcoin",
      "--other_agencies", "Flatland", "--notes", "this is a sample added proposal"],
     "20_anewproposal has been added in proposals\n"),
    (["helper", "a_expense", "159.18", "timbuktoo", "travel to timbuktoo",
      "--grants", "mrsec14", "dmref15", "--payee", "ashaaban",
      "--where", "bank", "--begin_date", "2020-06-20", "--end_date", "2020-06-25"],
     "2006as_timbuktoo has been added in expenses\n"),
    (["helper", "l_milestones", "--verbose"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_milestones", "--verbose", "--lead", "lyang"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_projecta", "--verbose", "--lead", "ascopatz"],
     "20sb_firstprojectum\n    status: proposed, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
     (["helper", "l_projecta", "--verbose", "--person", "ascopatz"],
     "20ly_newprojectum\n    status: started, begin_date: 2020-04-29, due_date: None, end_date: None, grant: SymPy-1.1\n    description: more work\n    team:\n        lead: lyang\n        group_members: ascopatz\n        collaborators: afriend\n20sb_firstprojectum\n    status: proposed, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_projecta", "--grant", "SymPy-1.1"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--grp_by_lead"],
     "lyang:\n    20ly_newprojectum\nascopatz:\n    20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--all"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--grp_by_lead", "-l", "ascopatz"],
     "ascopatz:\n    20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose"],
     "20ly_newprojectum\n    status: started, begin_date: 2020-04-29, due_date: None, end_date: None, grant: SymPy-1.1\n    description: more work\n    team:\n        lead: lyang\n        group_members: ascopatz\n        collaborators: afriend\n20sb_firstprojectum\n    status: proposed, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_projecta", "--ended", "--date", "2020-06-02"],
     "20sb_firstprojectum    My first projectum\n    Lead: ascopatz    Members: ascopatz    Collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_grants", "--current", "--date", "2020-05-25"],
     "sym2.0, awardnr: , acctn: , 2019-06-01 to 2030-12-31\n, awardnr: , acctn: GG012345, 2015-10-01 to 2025-09-30\n"
     ),
    (["helper", "l_members", "-v"],
     "Simon J. L. Billinge, professor | group_id: sbillinge\n"
     "    orcid: 0000-0002-9432-4248 | github_id: None\n"
     "Anthony Scopatz, professor | group_id: scopatz\n"
     "    orcid: 0000-0002-9432-4248 | github_id: ascopatz\n"
     ),
    (["helper", "l_members", "--filter", "name", "sco"],
     "scopatz    \n"
     ),
    (["helper", "l_members", "--filter", "name", "sco", "-v"],
     "Anthony Scopatz, professor | group_id: scopatz\n"
     "    orcid: 0000-0002-9432-4248 | github_id: ascopatz\n"
     ),
    (["helper", "l_contacts", "run", "--name", "ny", "--inst", "col",
      "--notes", "coffee", "--date", "2020-01-15", "--range", "2"],
     "Anthony B Friend  |  afriend  |  institution: Columbia University  |  email: friend@deed.com\n"
     ),
    (["helper", "l_contacts", "run", "--name", "ny", "--inst", "col",
      "--notes", "coffee", "--date", "2019-01-15", "--range", "2"],
     "\n"
     ),
    (["helper", "l_contacts", "run", "--verbose"],
     "Anthony B Friend\n"
     "    _id: afriend\n"
     "    email: friend@deed.com\n"
     "    institution: Columbia University\n"
     "    department: physics\n"
     "    notes:\n"
     "        -The guy I meet for coffee sometimes\n"
     "    aka:\n"
     "        -A. B. Friend\n        -AB Friend\n        -Tony Friend\n"
     ),
    (["helper", "u_milestone", "20sb_firstprojectum", "--index", "5",
      "--status", "converged", "--due_date", "2020-06-01"],
     "20sb_firstprojectum has been updated in projecta\n"
     ),
    (["helper", "u_milestone", "20sb"],
     "Projecta not found. Projecta with similar names: \n"
     "20sb_firstprojectum\n"
     "Please rerun the helper specifying the complete ID.\n"
     ),
    (["helper", "u_milestone", "20sb_firstprojectum"],
     "Please choose from one of the following to update/add:\n"
     "1. new milestone\n"
     "2. kickoff    due date: 2020-05-06    status: finished\n"
     "3. Project lead presentation    due date: 2020-05-20    status: proposed\n"
     "4. planning meeting    due date: 2020-05-27    status: proposed\n"
     "5. deliverable    due date: 2020-06-01    status: converged\n"
     ),
    (["helper", "u_milestone", "20sb_firstprojectum", "--verbose"],
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
     "4. planning meeting    due date: 2020-05-27:\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objetive: develop a detailed plan with dates\n"
     "     status: proposed\n"
     "     type: pr\n"
     "5. deliverable    due date: 2020-06-01:\n"
     "     audience: ['beginning grad in chemistry']\n"
     "     status: converged\n"
     ),
    (["helper", "u_logurl", "20sb", "--number", "1", "https://docs.google.com/document/d/1pQMFpuI"],
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
      "--notes", "Test note", "--aliases", "Friend", "--date", "2020-01-02"],
     "afriend has been added/updated in contacts\n"
     ),
    (["helper", "u_contact", "Anthony", "--date", "2020-01-02"],
     "Please rerun the helper by hitting up arrow and adding '-i list-index' to "
     "update the list item 'list-index', e.g., 'regolith helper eins -i 2'. For "
     "new contacts --name (-n) and --institution (-o) are required:\n"
     "1. Anthony as a new contact\n"
     "2. Anthony B Friend\n"
     "   id: afriend\n"
     "   email: friend@deed.com\n"
     "   institution: columbiau\n"
     "   department: physics\n"
     "   notes: ['The guy I meet for coffee sometimes', 'Test note']\n"
     "   aliases: ['A. B. Friend', 'AB Friend', 'Tony Friend', 'Friend']\n"
     ),
    (["helper", "u_contact", "Maria", "--date", "2020-01-02"],
     "Please rerun the helper by hitting up arrow and adding '-i list-index' to "
     "update the list item 'list-index', e.g., 'regolith helper eins -i 2'. For "
     "new contacts --name (-n) and --institution (-o) are required:\n"
     "1. Maria as a new contact\n"
     ),
    (["helper", "l_todo", "--id", "sbillinge", "--short_tasks"],
     "1. prepare the presentation\n"
     ),
    (["helper", "l_todo", "--id", "sbillinge", "--short_tasks", "65"],
     "1. read paper\n2. prepare the presentation\n"
     ),
    (["helper", "l_todo", "--verbose", "--id", "sbillinge", "--short_tasks"],
     "1. prepare the presentation\n     --notes: ['about 10 minutes', \"don't forget to upload to the website\"]\n     --due: 2020-07-29, importance:0, 30.0 min, start date: 2020-06-22\n"
     ),
    (["helper", "l_todo", "--id", "sbillinge"],
     "1. Simon: test\n2. Everyone: Clear out-of-date prums milestones.\n3. read paper\n4. prepare the presentation\n"
     ),
    (["helper", "l_todo", "-i", "wrong_id"],
     "The id you entered can't be found in people.yml.\n"
     ),
    (["helper", "l_todo", "--verbose", "--id", "sbillinge"],
     "1. Simon: test\n     --due: 2020-06-18, importance:1,  \n2. Everyone: Clear out-of-date prums milestones.\n     --due: 2020-06-18, importance:1,  \n3. read paper\n     --due: 2020-07-19, importance:2, 60.0 min, start date: 2020-06-15\n4. prepare the presentation\n     --notes: ['about 10 minutes', \"don't forget to upload to the website\"]\n     --due: 2020-07-29, importance:0, 30.0 min, start date: 2020-06-22\n"
     ),
    (["helper", "a_todo", "test a_todo", "10", "--id", "sbillinge", "--begin_date", "2020-07-06",  "--duration", "50", "--importance", "2", "--notes", "test notes 1", "test notes 2"],
     "The task \"test a_todo\" for sbillinge has been added in people collection.\n"
     ),
    (["helper", "finish_prum", "20sb_firstprojectum", "--end_date", "2020-07-01"],
     "20sb_firstprojectum status has been updated to finished\n"
     ),
    (["helper", "finish_prum", "20sb"],
     "Projectum not found. Projecta with similar names: \n"
     "20sb_firstprojectum     status:finished\n"
     "Please rerun the helper specifying the complete ID.\n"
     ),
    (["helper", "lister", "people"],
     "Results of your search:\nsbillinge    \nscopatz\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon"],
     "Results of your search:\n"
     "sbillinge\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon", "--return_fields", "name", "position"],
     "Results of your search:\nsbillinge    name: Simon J. L. Billinge    position: professor\n"),
    (["helper", "lister", "people", "--keys"],
     "Available keys:\n"
     "['_id', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
     "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
     "'github_id', 'google_scholar_url', 'hindex', 'home_address', 'initials', "
     "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
     "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
     "'title', 'todos']\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon", "--keys"],
     "Results of your search:\nsbillinge\n"
     "Available keys:\n"
     "['_id', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
     "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
     "'github_id', 'google_scholar_url', 'hindex', 'home_address', 'initials', "
     "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
     "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
     "'title', 'todos']\n"
     ),
    (["helper", "lister", "people", "--kv_filter", "name", "simon", "position", "singer"],
     "There are no results that match your search.\n"
     ),
    (["helper", "u_institution", "columbiau",
      "--aka", "ucolumbia", "Columbia University in the City of New York",
      "--dept_id", "mathematics", "--dept_name", "Department of Mathematics",
      "--dept_aka", "dept. of mathematics", "math department",
      "--school_id", "cc", "--school_name", "Columbia College", "--school_aka", "CC",
      "--date", "2020-01-01"],
     "columbiau has been updated/added in institutions\n"
     ),
    (["helper", "u_institution", "col"],
     "Please rerun the helper specifying '-n list-index' to update item number 'list-index':\n"
     "1. col as a new institution.\n"
     "2. columbiau      Columbia University.\n"),
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

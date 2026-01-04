"""Helper for adding a projectum to the projecta collection.

Projecta are small bite-sized project quanta that typically will result
in one manuscript.
"""

import datetime as dt

import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import DbHelperBase
from regolith.tools import all_docs_from_collection, get_pi_id, strip_str

# from regolith.schemas import MILESTONE_TYPES


TARGET_COLL = "projecta"


def subparser(subpi):
    date_kwargs = {}
    if isinstance(subpi, GooeyParser):
        date_kwargs["widget"] = "DateChooser"

    subpi.add_argument("name", type=strip_str, help="A short but unique name for the projectum", default=None)
    subpi.add_argument("lead", type=strip_str, help="id of the group lead or tbd", default=None)
    subpi.add_argument("-n", "--notes", type=strip_str, nargs="+", help="Anything to note", default=[])
    subpi.add_argument("-d", "--description", type=strip_str, help="Slightly longer description of the projectum")
    subpi.add_argument(
        "-c",
        "--collaborators",
        nargs="+",
        type=strip_str,
        help="list of outside collaborator ids separated by spaces, "
        "'aeinstein efermi'.  Builders will get the full names "
        "from the contacts collection",
    )
    subpi.add_argument(
        "-m",
        "--group-members",
        nargs="+",
        type=strip_str,
        help="list of group member ids, e.g., 'astudent acolleague'. "
        "Builders will get full names from people collection."
        "Do not add the lead or the group"
        "the pi who are added by default.",
    )
    subpi.add_argument(
        "-g",
        "--grants",
        type=strip_str,
        nargs="+",
        help="grant or (occasionally) list of grants that support this work",
    )
    subpi.add_argument(
        "-u", "--due-date", type=strip_str, help="proposed due date for the deliverable", **date_kwargs
    )
    subpi.add_argument(
        "--checklist", action="store_true", help="Use this to turn the prum into a paper submission" "checklist."
    )
    # Do not delete --database arg
    subpi.add_argument(
        "--database",
        type=strip_str,
        help="The database that will be updated.  Defaults to " "first database in the regolithrc.json file.",
    )
    # Do not delete --date arg
    subpi.add_argument(
        "--date",
        type=strip_str,
        help="The begin_date for the projectum  Defaults to " "today's date.",
        **date_kwargs,
    )
    return subpi


class ProjectumAdderHelper(DbHelperBase):
    """Helper for adding a projectum to the projecta collection.

    Projecta are small bite-sized project quanta that typically will
    result in one manuscript.
    """

    # btype must be the same as helper target in helper.py
    btype = "a_projectum"
    needed_colls = [f"{TARGET_COLL}", "groups", "people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(all_docs_from_collection(rc.client, rc.coll), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def db_updater(self):
        rc = self.rc
        if not rc.date:
            now = dt.date.today()
        else:
            now = date_parser.parse(rc.date).date()
        key = f"{rc.lead[:2]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError("This entry appears to already exist in the collection")
        else:
            pdoc = {}

        pdoc.update(
            {
                "begin_date": now,
                "log_url": "",
                "supplementary_info_urls": [],
                "name": rc.name,
                "pi_id": rc.pi_id,
                "lead": rc.lead,
                "notes": rc.notes,
            }
        )
        if rc.lead == "tbd":
            pdoc.update({"status": "proposed"})
        else:
            pdoc.update({"status": "started"})

        if rc.description:
            pdoc.update(
                {
                    "description": rc.description,
                }
            )
        if rc.grants:
            if isinstance(rc.grants, str):
                rc.grants = [rc.grants]
            pdoc.update({"grants": rc.grants})
        else:
            pdoc.update({"grants": ["tbd"]})
        if rc.group_members:
            if isinstance(rc.group_members, str):
                rc.group_members = [rc.group_members]
            pdoc.update({"group_members": rc.group_members})
        else:
            pdoc.update({"group_members": []})
        if rc.collaborators:
            if isinstance(rc.collaborators, str):
                rc.collaborators = [rc.collaborators]
            pdoc.update(
                {
                    "collaborators": rc.collaborators,
                }
            )
        else:
            pdoc.update(
                {
                    "collaborators": [],
                }
            )

        pdoc.update({"_id": key})
        pdoc.update(_set_deliverable(rc.due_date))
        pdoc.update(
            {
                "kickoff": {
                    "due_date": now + relativedelta(days=7),
                    "end_date": now + relativedelta(days=7),
                    "audience": ["lead", "pi", "group_members"],
                    "name": "Kick off meeting",
                    "objective": "introduce project to the lead",
                    "status": "finished",
                }
            }
        )
        pdoc.update({"milestones": []})

        if rc.checklist:
            pdoc = self._insert_checklists(pdoc, now)

        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return

    def _insert_checklists(self, pdoc, now):
        """Create manuscript checklist, one item as one milestone."""
        presubmission_checklist = [
            (
                "Create slide figures",
                "Create Inkscape graphics (Inkscape is preferable over ppt) for the slides "
                "and place in a ``figures`` directory in the slides directory. "
                "These may then be used either in beamer or ppt. "
                "Iterate with PI to convergence. (to get started with Inkscape download and install it, "
                "then run the program and navigate to Help-->Tutorials.  "
                "The first two ('Basic' and 'Shapes') should probably be enough for someone "
                "to get basic functionality.).",
            ),
            (
                "Create slides",
                "Create a 'slides' folder in the paper repo or a Google slides deck for a series of talk slides. "
                "Iterate the slide skeleton with PI to convergence. "
                "(For a beamer template: https://gitlab.thebillingegroup.com/talks/beamerTalkTemplate).",
            ),
            (
                "Create a highlight slide",
                "Create a 'highlight' folder in the paper repo. Create a single 'highlight' slide that describes "
                "the result following NSF/DOE guidelines. Place it in the 'highlight' folder. "
                "Iterate with PI to convergence (highlight templates and examples can be found in "
                "https://gitlab.thebillingegroup.com/papers/highlights)",
            ),
            (
                "Create public-summary",
                "Create a public summary in a text file. Place it in the 'highlight' folder. "
                "Iterate with PI to convergence. (The kudos template and example can be found at "
                "https://docs.google.com/document/d/1j4ZsM8zS_nZo03s7T48uwzDbh8xTPksAQM3ZLgJ-g-Y).",
            ),
            (
                "Add links to urls with supplementary info in the prum",
                "Add url links to raw or analyzed data and code that was used in the data analysis, "
                "and anything else, in gitlab or elsewhere into the 'supplementary_info_urls' field in the prum",
            ),
        ]

        submission_checklist = [
            (
                "Add paper to citations collection in regolith database",
                "If it will be submitted to a preprint server such as arxiv, put it in the citations collection "
                "in a public database, if the paper is not on a preprint server "
                "put the entry in the citations collection on a non-public "
                "(e.g., group) database Check, double check, and triple check "
                "that the tag for the grant is correct and the tags for the facilities are correct. "
                "Any questions, ask PI.",
            ),
            (
                "Create public facing supplementary information as needed",
                "Ask first before making things public, but any code or data "
                "that we want to publish as supplementary info should be put in a place "
                "where it can be made public or at least available to referees "
                "(e.g., in a repo on GitHub).",
            ),
            (
                "Make sure the public facing SI info has the right license",
                "check with the PI for the best license to put on this, "
                "but it will likely be some kind of creative commons license",
            ),
            (
                "Put url links to all open shared SI data repositorities into the 'supplementary_info_urls' field "
                "in the entry for this paper in the citations collection.",
                "the url links in supplementary_info_urls in the projecta collection are to internal data- "
                "and code- stores so future group members can find things. "
                "The fields in the citations collection should be public facing urls",
            ),
            (
                "Check the author list",
                "Check the author list. Last chance to check for missing authors. "
                "Does each author agree to submit to the specific journal? "
                "Make sure all authors have approved submission.",
            ),
            (
                "Check publisher accounts",
                "Check that all of the authors have accounts for the publisher you are submitting to "
                "(if possible) and that they have their ORCID IDs associated with their accounts "
                "(ie. for ACS, authors need to link their Paragon accounts with their ORCID IDs).",
            ),
            (
                "Check institution",
                "Is author's name, institution correct? Last chance to avoid embarrassing typos.",
            ),
            (
                "Check acknowledgement",
                "Are beamlines, grants, fundings properly acknowledged at the end of the paper? "
                "Double check this with PI and use the ackno statements in the Group Google group.",
            ),
            (
                "Check figures and tables",
                "Are all the figures, tables in the paper correct (the ones you intended)?",
            ),
            (
                "Check figure captions",
                "Check the Figure captions for errors. If they refer to a green line, is the relevant line green, "
                "and so on.",
            ),
            (
                "Check figure axis labels",
                "Check that the figure axis labels are correctly labeled. "
                "Make sure it doesn't say G when F is plotted. Make sure the units are correct. "
                "Make sure it says 'G (A^-2)' and NOT 'G(r)' (common mistake).",
            ),
            (
                "Check table captions",
                "Check the table caption is correct. Are all the items in the table "
                "properly defined in the caption. If it is a crystal structure, are the space group "
                "and special positions mentioned in the caption? Is all the info correct?",
            ),
            ("Check numbers in the table", "Check all the numbers in the tables for errors."),
            (
                "Check any question marks",
                "Check all the question marks in the text. Is there any 'FIG.???' or unrecognized character?",
            ),
            (
                "Check figure references",
                "Check references to the all figures and tables. "
                "Does reference to Figure 4 refer to the right figure for example.",
            ),
            (
                "Check references",
                "Go through the references and find all the errors. Correct errors in the bibliographic database "
                "(citations.yml, or the Zotero collection, for example), not in the local bib file. "
                "Did all the journal names compile correctly? Are they all consistently in abbreviated form "
                "(or full form if that is the style, though that is rare). Volume, "
                "year and page numbers appear for all references? Hard to find errors in these numbers, "
                "but when you do, definitely correct the database!",
            ),
            ("Check reference style", "Is reference's style in accordance with journal's requirement?"),
            (
                "Check journal submission requirements",
                "Check the journal submission requirements for cover letters, table of contents pictures, "
                "list of referees, etc..",
            ),
            ("Check arxiv", "Check with PI; will the paper be submitted to arXiv?"),
            (
                "Get approval",
                "Get final approval from all authors for the final version of the manuscript, cover letter, "
                "referees list, etc., submission to arXiv if appropriate.",
            ),
            (
                "Check open access",
                "Check with coauthors if the paper should be submitted open access. "
                "Do not guess on this one as there may be financial consequences",
            ),
            (
                "Check cover letter",
                "In the cover letter, does it contain editor-in-chief's name and institution "
                "(usually at the top left of the letter) ? Is the content of letter concise and eye-catching? "
                "Are (three) suggested reviewers' information in the letter?",
            ),
            (
                "Do a trial submission",
                "Go through the online submission process finding out all the questions that you will be asked, "
                "but don't actually press submit, and then check with the PI about the right answers",
            ),
            ("Commit and push", "Commit all the changes to your local repo, then push the changes to gitlab."),
            (
                "Create a PR of the updated citations entry",
                "Create a PR to merge to the billingeGroup repository and work to get it merged",
            ),
            ("Submit to journal", "Go ahead and make the submission, usually online."),
            (
                "Push a tag",
                "If during the submission process you need to make any changes, do it in your local repo and "
                "make another commit and push. When the submission is finalized, tag the repo that points to "
                "THIS VERSION IS THE SUBMITTED VERSION. create the submission tag.  If the current version of "
                "your local repo is the submitted version, type, e.g., `git tag -l` to list previous tags "
                "(try and keep the tag name formatting consistent) "
                "`git tag -a 20180525PRLsubmitted -m <initial submission to PRL>` `git push origin <tag_name>`.",
            ),
            (
                "Modify tag if needed",
                "If you forgot to tag and made some changes to the repo "
                "and need to point the tag to an earlier version, or want to view all the different tags, "
                "or do some other complicated thing, more info about tagging git repos is here: "
                "https://git-scm.com/book/en/v2/Git-Basics-Tagging",
            ),
            ("Submit to arxiv if needed", "Submit to arxiv if appropriate."),
            (
                "Push an arxiv tag",
                "Make a new tag of the version submitted to arXiv with the name arXivSubmitted20170610.",
            ),
            (
                "Check db errors",
                "In your rg-db-public/local directory, run `regolith build publist --people lyang` "
                "(replace `lyang` with your own name ID in the group) to make sure "
                "that you publist is building properly. Make sure that the publication appears correctly "
                "with no errors and fix anything. If there are problems with the latex building, "
                "run the commands with --no-pdf, which yields the latex source but doesn't build it, then build "
                "the latex manually. The complied tex and pdf files are located in the `_build` folder. "
                "If any problem about installing regolith and databases, please refer to "
                "[rg-db-group wiki]("
                "https://github.com/Billingegroup/rg-db-group/wiki/Set-up-regolith-and-databases).",
            ),
            ("Get arxiv reference", "Wait a day to get the full arXiv reference."),
            ("Email coauthors", "Send an email to coauthors letting them know the arXiv citation information."),
            ("Ask PI if anything unfinished", "Ask PI about any items unfinished."),
            ("Email PI", "Email PI if finish the above."),
        ]

        resubmission_checklist = [
            (
                "Work on the changes",
                "Make changes to the manuscript in the repo. You don't need to save it to a new name or anything "
                "because we can recover the old version by checking out the tagged version.",
            ),
            (
                "Write rebuttal letter",
                "Write a proper rebuttal letter based on reviewers' comments and place in the repo. "
                "In this letter address all of the referee's points, one by one. Place a copy of "
                "the referee's comments in the repo. Give it a unique filename in case "
                "there are more referee comments from later submissions!",
            ),
            (
                "Check author list",
                "This is a good time to check that the author list is correct "
                "(don't need to add anyone or remove anyone) and that the acknowledgements "
                "have been done correctly, the figures are correct, the figure captions and table captions "
                "are correct and all the figures and tables are correctly referenced, and there are "
                "no compilation errors. Check all references for errors and update any "
                "'unpublished' references if they have been published.",
            ),
            (
                "Diff the changes",
                "create a diff.pdf file that shows changes to the manuscript between the version in the tag of "
                "the previous submission and the current version, and include this in the resubmission.",
            ),
            (
                "Send to coauthors",
                "Send the final version to your coauthors. Tell them you will 'submit on' "
                "where is somewhere around 48 hours later and ask for any final corrections etc. from them. "
                "Offer them the chance to extend the deadline if they need more time, "
                "i.e., write 'if you need more time, lease let me know.' "
                "However, it is assumed that all the authors have been involved in the correction process up to "
                "this point so they only have to give it one final thought...",
            ),
            ("Git commit changes", "Commit all the changes to your local repo, then push the changes to gitlab."),
            ("Resubmit", "Resubmit following the instructions of the journal."),
            (
                "Commit any additional changes",
                "If during the submission process you need to make any changes, do it in your local repo and "
                "make another commit and push.",
            ),
            ("Push a resubmission tag", "Make a new resubmission tag (see above for details)"),
            (
                "Check db entry",
                "Check the entry in citations.yml doesn't need to be updated, and update if it does.",
            ),
            ("Ask PI if anything unfinished", "Ask PI about any items unfinished."),
            ("Email PI", "Email PI if finish the above."),
        ]

        accepted_checklist = [
            (
                "Share the news",
                "Congratulations on the acceptance of the paper. Let all coauthors know the great news!",
            ),
            (
                "Share with BNL if needed",
                "If it is a BNL paper (check with PI, but it should acknowledge BNL funding-not just beamtime), "
                "send a pdf copy of the accepted version of the paper from the repo to Arlene at BNL to get "
                "a BNL publication number.  If you are not sure what this means, ask PI",
            ),
            (
                "Share the proof",
                "When you receive the proofs, share them quickly with all the authors. Request comments back "
                "in 24 hours. Proofs should be responded to within 48 hours in normal circumstances.",
            ),
            ("Respond the editor", "Go through and answer any questions from the editor."),
            (
                "Check author names",
                "Last chance to check that all the authors' names are correct and there are no missing authors.",
            ),
            ("Check institutions", "Check all authors' institutions are correct."),
            (
                "Check acknowledgement",
                "Make sure that all funding and all beamlines used are correctly acknowledged. "
                "Usually this is done by the bosses, but more eyes catch more mistakes.",
            ),
            (
                "Update the db entry",
                "In citations.yml, (the reference should have been added during the submission step) double check "
                "the grants{}, facilities{}, nb{} field entries. Any questions, ask PI. Put 'to be published' "
                "in the note{} section. If it has not been submitted to arxiv before, move the entry "
                "from rg-db-group to rg-db-public github repo. Otherwise, it should be at rg-db-public already. "
                "Create a PR to merge to the billingeGroup repository for edits if necessary.",
            ),
            (
                "Check db errors",
                "In your rg-db-public/local directory, run `regolith build publist --people lyang` "
                "(replace lyang with your name) to make sure that you publist is building properly. "
                "Make sure that the publication appears correctly with no errors and fix anything. If there are "
                "problems with the latex building, run the commands with --no-pdf, "
                "which yields the latex source but doesn't build it, then build the latex manually. "
                "If any problem about installing regolith and databases, please refer to "
                "[rg-db-group wiki]("
                "https://github.com/Billingegroup/rg-db-group/wiki/Set-up-regolith-and-databases).",
            ),
            (
                "Check figures and tables",
                "Are all the figures, tables in the paper correct (the ones you intended)?",
            ),
            (
                "Check the figure caption",
                "Check the Figure captions for errors. If they refer to a green line, is the relevant line green, "
                "and so on.",
            ),
            (
                "Check figure axis labels",
                "Check that the figure axis labels are correctly labeled. Make sure it doesn't say G when "
                "F is plotted. Make sure the units are correct. Make sure it says 'G (A^-2)' and NOT 'G(r)' "
                "(common mistake)",
            ),
            (
                "Check table captions",
                "Check the table caption is correct. Are all the items in the table "
                "properly defined in the caption. If it is a crystal structure, are the space group "
                "and special positions mentioned in the caption? Is all the info correct?",
            ),
            ("Check numbers in the table", "Check all the numbers in the tables for errors."),
            (
                "Check figure references",
                "Check references to the all figures and tables. Does reference to Figure 4 refer to "
                "the right figure for example",
            ),
            (
                "Check references",
                "Go through the references and find all the errors. Correct errors in the bibliographic database "
                "AS WELL AS on the proofs the manuscript. Did all the journal names compile correctly? "
                "Are they all consistently in abbreviated form "
                "(or full form if that is the style, though that is rare). Volume, year and page numbers "
                "appear for all references? Hard to find errors in these numbers, but when you do, "
                "definitely correct the database!",
            ),
            (
                "Check unpublished references",
                "If any references are listed as unpublished, on arXiv or submitted or something, "
                "check if they have appeared and give the full reference if at all possible. To do this, "
                "update the bibliographic database (e.g., citations.yml) with this information and then "
                "recompile the references, then copy paste the new bbl file back into the TeX source.",
            ),
            (
                "Check reference titles if needed",
                "If the manuscript style has titles in the references, make sure there are no capitalization "
                "or other compilation errors. Again, correct these in the database using {braces} around words "
                "where you want to preserve the capitalization as well as on the proof.",
            ),
            (
                "Read the paper",
                "Finally, after you have done all these 'mechanical' checks, "
                "read through the paper and try and find any typos or other problems. "
                "Resist the temptation to do any rewriting here...you are looking for misspellings "
                "and missing or extra words and so on.",
            ),
            (
                "Apply corrections from coauthors",
                "Collect all the corrections from the other authors "
                "and add any additional ones to the proof and return it.",
            ),
            ("Email coauthors", "Send an email to your coauthors that this was successfully resubmitted."),
            (
                "Revisit talk slides",
                "Revisit the set of talk slides that summarize the result in a few slides "
                "if they need to be updated. Iterate with PI to convergence.",
            ),
            (
                "Revisit the highlight slide",
                "Create a single 'highlight' slide that describes the result following NSF/DOE guidelines. "
                "Place it in the 'highlight' folder. Iterate with PI to convergence "
                "(highlight templates and examples can be found in "
                "https://gitlab.thebillingegroup.com/highlights/highlightTemplate)",
            ),
            (
                "Check the url links to all open shared SI data repositorities "
                "in the 'supplementary_info_urls' field in the entry for this paper "
                "in the citations collection. make sure they work and the data are accessible.",
            ),
            (
                "Create web news",
                "Create a web news story for thebillingegroup.com site. Place it in the 'highlight' folder. "
                "Iterate with PI to convergence",
            ),
            (
                "Revisit kudos",
                "Revisit the Kudos summary if it needs to be updated. Iterate with PI to convergence.",
            ),
            ("Ask PI if anything unfinished", "Ask PI about any items unfinished."),
            ("Email PI", "Email PI if finish the above."),
        ]

        published_checklist = [
            ("Congrats", "Phew, it is over! Pat yourself on the back and celebrate!"),
            ("Let coauthors know", "Let your coauthors know the link to the final paper and the final reference."),
            (
                "Update db entry",
                "Update citations.yml at rg-db-public github repo with the correct reference information. "
                "Commit your edited citations.yml and create a PR to merge to the billingeGroup repository.",
            ),
            (
                "Check db entry",
                "CAREFULLY double and triple check the meta-data associated with the paper in citations.yml:",
            ),
            (
                "Check grants in the db entry",
                "grant{} lists just the billinge-group grants that appeared in the acknowledgement section. "
                "They have standard abbreviations that are listed at the top of the citations.yml file, "
                "e.g., fwp, EFRC10, etc.. Use the right standard or the whole system becomes broken! "
                "If not sure.....ask PI. List all grants in a comma-separated list.",
            ),
            (
                "Check the facility in the db entry",
                "facility{} is every beamline that was used for data collection. "
                "Again, use the standard abbreviations at the top of the file. "
                "Use two levels of granularity for each, so X17A would be: 'nsls, x17a', "
                "if X17A and X7B were used it would be 'nsls, x17a, x7b' and so on.",
            ),
            (
                "Check the nb in the db entry nb is some other tags, "
                "also listed at the top of the file. 'art' for a regular article and 'hilite' "
                "if it is one of our top top papers are the most common.",
            ),
            (
                "Check the tags in the db entry",
                "tags should reflect the content so we can automatically build reading lists by subject. "
                "Most papers are PDF papers, so no need to say pdf, be more targeted.",
            ),
            (
                "Add the url link to the SI at the journal to the 'supplementary_info_urls' field "
                "in the entry for this paper in the citations collection.",
                "Don't necessarily remove the others if they are still open and public. "
                "It is also ok to put URLs to our data repositories as part of the SI in the paper",
            ),
            (
                "Check db errors",
                "In your rg-db-public/local directory, run `regolith build publist --people lyang` "
                "(replace lyang with your name) to make sure that you publist is building properly. "
                "Make sure that the publication appears correctly with no errors and fix anything. If there are "
                "problems with the latex building, run the commands with --no-pdf, which yields the latex source "
                "but doesn't build it, then build the latex manually.",
            ),
            (
                "Add/update to Zotero",
                "Add or update the published reference to the billinge-group-bib folder "
                "in our group Zotero account",
            ),
            (
                "Finalize the highlight slide",
                "Make a highlight of your work and put it in gitlab/highlights "
                "(if not done already during the accepted paper checklist). "
                "Look in there for standards to work from. This is an important activity. "
                "Now you have done your great work, this is how you can advertise it to others. "
                "Top papers we send these highlights to the funding agencies. "
                "Iterate the highlight with PI till it is converged.",
            ),
            (
                "Finalize figures and talk slides",
                "Make figures and talk slides that will be used in talks "
                "and place these on gitlab on talks/figures. Iterate this with PI till it is converged.",
            ),
            (
                "Update arXiv if necessary",
                "If the paper was listed on a preprint server like arXiv, submit a note to arXiv that the paper "
                "has appeared and give the full reference. If the journal copyright allows "
                "you can post the published version here, but normally that is not allowed! "
                "Still, it is important that people who find the paper on arXiv "
                "get directed to the correct reference.",
            ),
            ("Ask PI if anything unfinished", "Ask PI about any items unfinished."),
            ("Email PI", "Email PI if finish the above."),
        ]

        checklistm_list = []
        checklist_delay_days = (
            [7] * len(presubmission_checklist)
            + [14] * len(submission_checklist)
            + [74] * len(resubmission_checklist)
            + [134] * len(accepted_checklist)
            + [194] * len(published_checklist)
        )
        checklist_names = (
            ["presubmission"] * len(presubmission_checklist)
            + ["submission"] * len(submission_checklist)
            + ["resubmission"] * len(resubmission_checklist)
            + ["accepted"] * len(accepted_checklist)
            + ["published"] * len(published_checklist)
        )
        checklists = presubmission_checklist + submission_checklist + accepted_checklist + published_checklist
        for (name, objective), checklist_name, delay_days in zip(
            checklists, checklist_names, checklist_delay_days
        ):
            checklistm = {
                "due_date": now + relativedelta(days=delay_days),
                "name": f"{checklist_name} - {name}",
                "objective": objective,
                "audience": [],
                "notes": [],
                "status": "converged",
                "type": "mergedpr",
            }
            checklistm_list.append(checklistm)

        pdoc.update({"milestones": checklistm_list})

        # update the deliverable to fit checklist prum
        pdoc.update(
            {
                "deliverable": {
                    "due_date": now + relativedelta(days=checklist_delay_days[-1]),
                    "audience": ["PI"],
                    "success_def": "audience is happy",
                    "scope": ["checklist", "All publication data and metadata are correct and complete"],
                    "platform": "regolith publication collection in rg-db-public",
                    "roll_out": ["PI merging PRs"],
                    "status": "converged",
                }
            }
        )

        # update the kickoff to fit checklist prum
        pdoc.update(
            {
                "kickoff": {
                    "due_date": now,
                    "audience": ["lead", "pi", "group_members"],
                    "name": "Kick off meeting",
                    "objective": "introduce project to the lead",
                    "status": "finished",
                }
            }
        )
        return pdoc


def _set_deliverable(due_date_str, pattern=None):
    due_date = dt.date.fromisoformat(due_date_str)
    if pattern == "software":
        pu_deliverable = {
            "deliverable": {
                "due_date": due_date,
                "audience": [
                    "Who will use the software or read the paper? "
                    "Your target audience. e.g., beginning grad in chemistry"
                ],
                "success_def": "audience is happy",
                "scope": [
                    "If this is a software release, list any use-cases that are in "
                    "scope. These may be located in the Gdoc associated with the "
                    "prum.  Otherwise include some other kind of scope description "
                    "of what is in and what is not",
                    "If this is a science paper summarize: ",
                    "the scientific question that is being answered",
                    "any hypotheses that will be tested to answer it",
                    "the approach that will be taken",
                ],
                "platform": "description of how and where the audience will access "
                "the deliverable.  The journal where it will be submitted "
                "if it is a paper. Whether it is a web-app, or which "
                "operating systems will be supported, for software",
                "roll_out": [
                    "steps that the audience will take to access and interact with the deliverable",
                    "leave as empty list for paper submissions",
                ],
                "status": "proposed",
            }
        }
    else:
        pu_deliverable = {
            "deliverable": {
                "due_date": due_date,
                "audience": [],
                "success_def": "",
                "scope": [],
                "platform": "",
                "roll_out": [],
                "status": "proposed",
            }
        }
    return pu_deliverable


# secondm = {'due_date': now + relativedelta(days=21),
#            'name': 'Example milestone',
#            'objective': 'This acts as an example milestone. It shows how '
#                         'to construct your milestones.  It should be deleted '
#                         'before depositing the prum.',
#            'audience': ["update the audience as required, but it is "
#                         "often lead, pi and group_members (see below). "
#                         "these resolve to their values defined elsewhere.  "
#                         "If putting in people's names use their ids where "
#                         "possible and they will be looked for in the "
#                         "people and contacts collections.",
#                         'lead', 'pi', 'group_members'],
#            'status': 'proposed',
#            'notes': ["() get a clear picture of the deliverable and what "
#                      "needs to be done to get there.  Have discussions "
#                      "with group members to develop ideas.  Propose them "
#                      "even if you are not sure, you will get feedback. "
#                      "This is the process.",
#                      "() edit the template 'deliverable' to reflect that.",
#                      "() chart out milestones at a high level first working "
#                      "back from the deliverable.  'To deliver that "
#                      "(deliverable) I have to do this, this and this, and "
#                      "to deliver it by then I have to do these things by "
#                      "these dates.'",
#                      f"() then write the detailed milestones, turning each "
#                      f"one into a deliverable that is captured in the type "
#                      f"field.  Allowed values for milestone types are: "
#                      f"{*MILESTONE_TYPES,}.  If you are tempted to use 'other' "
#                      f"think more about the milestone objective, you "
#                      f"probably haven't defined it well enough in your head.",
#                      "() Think carefully about the deliverable date.  "
#                      "Can you hit it?  If not, change it so you can hit "
#                      "it.  You may have to adjust your final deliverable date "
#                      "but discuss this with the team, because scope could also "
#                      "be reduced rather than pushing off final deliverable.  "
#                      "When you are comfortable with the due date, and it has "
#                      "been reviewed, make the appoint on the calendar, for "
#                      "example, if it is a meeting or presentation, send "
#                      "schedule it now.",
#                      "() within each milestone, make a todo list (this "
#                      "is a todo-list) in the notes field.  A todo is a "
#                      "note prepended by () (no space in the middle).  These are the smaller "
#                      "tasks you will have to do to complete the milestone.  "
#                      "When you complete them turn () in to (x).",
#                      "() Iterate all these with your team/advisor maybe "
#                      "in a Google doc or on Slack to make sure you are "
#                      "on the right track.  To converge this shoot for "
#                      "multiple round-trips per day.",
#                      "() using u_milestones in helper_gui, or "
#                      "otherwise, get them entered into the prum and the "
#                      "prum deposited.",
#                      "() by the time the edited prum is submitted, set "
#                      "all the statuses to converged or started, and "
#                      "delete this example milestone.",
#                      "() later, when you finish a milestone use "
#                      "u_milestones or editing in the yaml "
#                      "file set status to finished and add an end_date, "
#                      "and fill in the progress section. This should be "
#                      "brief but just links to a brief text description "
#                      "of the outcome that would be suitable for a grant "
#                      "annual report, and any url links to "
#                      "presentations or related docs.  Link to specific "
#                      "files of relevance to this milestone not general docs and repos.",
#            ],
#            "progress": {'text': 'write text here capturing how the milestone '
#                                 'is progressing, but at the least when the milestone '
#                                 'closes.  The goal of this is that it will be '
#                                 'printed as a progress report for a grant '
#                                 'so write it as if it will be read by an external '
#                                 'person. It doesn't have to describe the whole prum '
#                                 'but clearly show the progress that has been made. '
#                                 'It can be multiple paragraphs or a short statement'
#                                 'depending on the situation',
#                         'slides_urls': ["<replace with a URL to, for example, "
#                                        "a Gslides slide deck "
#                                        "with useful figures in it, or a Gdoc "
#                                        "with more complicated info like tables "
#                                        "or something. This is for the PI to "
#                                        "be able to find quality content to augment "
#                                        "the report>","<replace with another URL if "
#                                                      "more than one is needed>"]},
#            'type': 'meeting',
#            'uuid': get_uuid()
# }
#
# secondm = {
#     "due_date": now + relativedelta(days=21),
#     "name": "Kickoff meeting",
#     "objective": "Prum Lead understands the project deliverables " "and goals",
#     "audience": ["lead", "pi", "group_members"],
#     "status": "converged",
#     "notes": [
#         "() Schedule the meeting",
#         "() Have the meeting, take good notes",
#         "() Update the prum milestones with plan",
#     ],
#     "progress": {"text": "", "slides_urls": []},
#     "type": "meeting",
#     "uuid": get_uuid(),
# }

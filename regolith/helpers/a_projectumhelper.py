"""Helper for adding a projectum to the projecta collection.

   Projecta are small bite-sized project quanta that typically will result in
   one manuscript.
"""
import datetime as dt
import dateutil.parser as date_parser
from dateutil.relativedelta import relativedelta
import sys

from regolith.helpers.basehelper import DbHelperBase
from regolith.fsclient import _id_key
from regolith.tools import (
    all_docs_from_collection,
    get_pi_id,
)

TARGET_COLL = "projecta"
ALLOWED_TYPES = ["nsf", "doe", "other"]
ALLOWED_STATI = ["proposed", "started", "finished", "back_burner", "paused",
                 "cancelled"]
MILESTONES_ALLOWED_STATI = ["proposed", "scheduled", "finished", "cancelled"]


def subparser(subpi):
    subpi.add_argument("name", help="A short but unique name for the projectum",
                       default=None)
    subpi.add_argument("lead", help="id of the group lead or tbd",
                       default=None)
    # Do not delete --database arg
    subpi.add_argument("--database",
                       help="The database that will be updated.  Defaults to "
                            "first database in the regolithrc.json file."
                       )
    # Do not delete --date arg
    subpi.add_argument("--date",
                       help="The begin_date for the projectum  Defaults to "
                            "today's date."
                       )
    subpi.add_argument("-d", "--description",
                       help="Slightly longer description of the projectum"
                       )
    subpi.add_argument("-c", "--collaborators", nargs="+",
                       help="list of outside collaborators who should  be in contacts"
                            "collection"
                       )
    subpi.add_argument("-m", "--group_members", nargs="+",
                       help="list of group members other than the lead who are involved"
                       )
    subpi.add_argument("-g", "--grants", nargs="+",
                       help="grant or (occasionally) list of grants that support this work"
                       )
    subpi.add_argument("-u", "--due_date",
                       help="proposed due date for the deliverable"
                       )
    subpi.add_argument("--checklist", action='store_true',
                       help="Create manuscript checklist if specified"
                       )
    return subpi


class ProjectumAdderHelper(DbHelperBase):
    """Helper for adding a projectum to the projecta collection.

       Projecta are small bite-sized project quanta that typically will result in
       one manuscript.
    """
    # btype must be the same as helper target in helper.py
    btype = "a_projectum"
    needed_dbs = [f'{TARGET_COLL}', 'groups', 'people']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.pi_id = get_pi_id(rc)
        rc.coll = f"{TARGET_COLL}"
        if not rc.database:
            rc.database = rc.databases[0]["name"]
        gtx[rc.coll] = sorted(
            all_docs_from_collection(rc.client, rc.coll), key=_id_key
        )
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
        if not rc.due_date:
            due_date = now + relativedelta(years=1)
        else:
            due_date = date_parser.parse(rc.due_date).date()
        key = f"{rc.lead[:2]}_{''.join(rc.name.casefold().split()).strip()}"

        coll = self.gtx[rc.coll]
        pdocl = list(filter(lambda doc: doc["_id"] == key, coll))
        if len(pdocl) > 0:
            raise RuntimeError(
                "This entry appears to already exist in the collection")
        else:
            pdoc = {}

        pdoc.update({
            'begin_date': now,
            'log_url': '',
            'name': rc.name,
            'pi_id': rc.pi_id,
            'lead': rc.lead,
        })
        if rc.lead == "tbd":
            pdoc.update({
                'status': 'proposed'
            })
        else:
            pdoc.update({
                'status': 'started'
            })

        if rc.description:
            pdoc.update({
                'description': rc.description,
            })
        if rc.grants:
            if isinstance(rc.grants, str):
                rc.grants = [rc.grants]
            pdoc.update({'grants': rc.grants})
        else:
            pdoc.update({'grants': ["tbd"]})
        if rc.group_members:
            if isinstance(rc.group_members, str):
                rc.group_members = [rc.group_members]
            pdoc.update({'group_members': rc.group_members})
        else:
            pdoc.update({'group_members': []})
        if rc.collaborators:
            if isinstance(rc.collaborators, str):
                rc.collaborators = [rc.collaborators]
            pdoc.update({
                'collaborators': rc.collaborators,
            })
        else:
            pdoc.update({
                'collaborators': [],
            })

        pdoc.update({"_id": key})
        pdoc.update({"deliverable": {
            "due_date": due_date,
            "audience": ["beginning grad in chemistry"],
            "success_def": "audience is happy",
            "scope": [
                "UCs that are supported or some other scope description if it software",
                "sketch of science story if it is paper"],
            "platform": "description of how and where the audience will access the deliverable.  journal if it is a paper",
            "roll_out": [
                "steps that the audience will take to access and interact with the deliverable",
                "not needed for paper submissions"],
            "status": "proposed"}
        })
        pdoc.update({"kickoff": {
            "due_date": now + relativedelta(days=7),
            "audience": ["lead", "pi", "group_members"],
            "name": "Kick off meeting",
            "objective": "introduce project to the lead",
            "status": "proposed"
        }})
        secondm = {'due_date': now + relativedelta(days=21),
                   'name': 'Project lead presentation',
                   'objective': 'to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.',
                   'audience': ['lead', 'pi', 'group_members'],
                   'status': 'proposed',
                   'type': 'meeting'
                   }
        pdoc.update({"milestones": [secondm]})

        if rc.checklist:
            pdoc = self.insert_checklists(pdoc, now)


        rc.client.insert_one(rc.database, rc.coll, pdoc)

        print(f"{key} has been added in {TARGET_COLL}")

        return

    def insert_checklists(self, pdoc, now):
        """Create manuscript checklist, one item as one milestone."""
        presubmission_checklist = [
            ("Create slide figures", "Create Inkscape graphics (Inkscape is preferrable over ppt) for the slides and place in a ``figures`` directory in the slides directory. These may then be used either in beamer or ppt. Iterate with Simon to convergence. (to get started with Inkscape download and install it, then run the program and navigate to Help-->Tutorials.  The first two ('Basic' and 'Shapes') should probably be enough for someone to get basic functionality.)."),
            ("Create slides", "Create a 'slides' folder in the paper repo or a Google slides deck for a series of talk slides. Iterate the slide skeleton with Simon to convergence. (For a beamer template: https://gitlab.thebillingegroup.com/talks/beamerTalkTemplate)."),
            ("Create a highlight slide", "Create a 'highlight' folder in the paper repo. Create a single 'highlight' slide that describes the result following NSF/DOE guidelines. Place it in the 'highlight' folder. Iterate with Simon to convergence (highlight templates and examples can be found in https://gitlab.thebillingegroup.com/papers/highlights)"),
            ("Create public-summary", "Create a public summary in a text file. Place it in the 'highlight' folder. Iterate with Simon to convergence. (The kudos template and example can be found at https://docs.google.com/document/d/1j4ZsM8zS_nZo03s7T48uwzDbh8xTPksAQM3ZLgJ-g-Y/edit?usp=sharing)."),
        ]

        submission_checklist = [
            ("Check the author list", "Check the author list. Last chance to check for missing authors. Does each author agree to submit to the specific journal? Make sure all authors have approved submission."),
            ("Check publisher accounts", "Check that all of the authors have accounts for the publisher you are submitting to (if possible) and that they have their ORCID IDs associated with their accounts (ie. for ACS, authors need to link their Paragon accounts with their ORCID IDs)."),
            ("Check institution", "Is author's name, institution correct? Last chance to avoid embarrassing typos."),
            ("Check acknowledgement", "Are beamlines, grants, fundings properly acknowledged at the end of the paper? Double check this with Simon and use the ackno statements in the Group Google group."),
            ("Check figures and tables", "Are all the figures, tables in the paper correct (the ones you intended)?"),
            ("Check figure captions", "Check the Figure captions for errors. If they refer to a green line, is the relevant line green, and so on."),
            ("Check figure axis labels", "Check that the figure axis labels are correctly labeled. Make sure it doesn't say G when F is plotted. Make sure the units are correct. Make sure it says 'G (A^-2)' and NOT 'G(r)' (common mistake)."),
            ("Check table captions", "Check the table caption is correct. Are all the items in the table properly defined in the caption. If it is a crystal structure, are the space group and special positions mentioned in the caption? Is all the info correct?"),
            ("Check numbers in the table", "Check all the numbers in the tables for errors."),
            ("Check any question marks", "Check all the question marks in the text. Is there any 'FIG.???' or unrecognized character?"),
            ("Check figure references", "Check references to the all figures and tables. Does reference to Figure 4 refer to the right figure for example."),
            ("Check references", "Go through the references and find all the errors. Correct errors in the bibliographic database (citations.yml, or the Zotero collection, for example), not just in the local bib file. Did all the journal names compile correctly? Are they all consistently in abbreviated form (or full form if that is the style, though that is rare). Volume, year and page numbers appear for all references? Hard to find errors in these numbers, but when you do, definitely correct the database!"),
            ("Check reference style", "Is reference's style in accordance with journal's requirement?"),
            ("Check journal submission requirements", "Check the journal submission requirements for cover letters, table of contents pictures, list of referees, etc.."),
            ("Check arxiv", "Check with Simon; will the paper be submitted to arXiv?"),
            ("Get approval", "Get final approval from all authors for the final version of the manuscript, cover letter, referees list, etc., submission to arXiv if appropriate."),
            ("Check cover letter", "In the cover letter, does it contain editor-in-chief's name and institution (usually at the top left of the letter) ? Is the content of letter concise and eye-catching? Are (three) suggested reviewers' information in the letter?"),
            ("Inser bbl", "If it is LaTeX, insert the .bbl file into the main tex file and comment out the \\thebibliography and \\bibliographystyle lines."),
            ("Commit and push", "Commit all the changes to your local repo, then push the changes to gitlab."),
            ("Submit to journal", "Go ahead and make the submission, usually online."),
            ("Push a tag", "If during the submission process you need to make any changes, do it in your local repo and make another commit and push. When the submission is finalized, tag the repo that points to THIS VERSION IS THE SUBMITTED VERSION. create the submission tag.  If the current version of your local repo is the submitted version, type, e.g., `git tag -l` to list previous tags (try and keep the tag name formatting consistent) `git tag -a 20180525PRLsubmitted -m <initial submission to PRL>` `git push origin <tag_name>`."),
            ("Modify tag if needed", "If you forgot to tag and made some changes to the repo and  need to point the tag to an earlier version, or want to view all the different tags, or do some other complicated thing, more info about tagging git repos is here: https://git-scm.com/book/en/v2/Git-Basics-Tagging"),
            ("Submit to arxiv if needed", "Submit to arxiv if appropriate."),
            ("Push an arxiv tag", "Make a new tag of the version submitted to arXiv with the name arXivSubmitted20170610."),
            ("Get arxiv reference", "Wait a day to get the full arXiv reference."),
            ("If submitted to arxiv, enter in citations collection in rg-db-public", "If submit to arxiv, create an entry of the paper in citations.yml at rg-db-public billingeGroup public github repository.  Check, double check, and triple check that the tag for the grant is correct and the tags for the facilities are correct. Fill in the arXiv citation information in citations.yml in the bibliography reference. Any questions, ask Simon. Create a PR to merge to the billingeGroup repository."),
            ("If not submitted to arxiv, enter in citations collection in rg-db-group", "If not submit to arxiv, create an entry of the paper in citations.yml at rg-db-group billingeGroup private github repository.  Check, double check, and triple check that the tag for the grant is correct and the tags for the facilities are correct.  Any questions, ask Simon. Create a PR to merge to the billingeGroup repository."),
            ("Check db errors", "In your rg-db-public/local directory, run `regolith build publist --people lyang` (replace `lyang` with your own name ID in the group) to make sure that you publist is building properly. Make sure that the publication appears correctly with no errors and fix anything. If there are problems with the latex building, run the commands with --no-pdf, which yields the latex source but doesn't build it, then build the latex manually. The complied tex and pdf files are located in the `_build` folder. If any problem about installing regolith and databases, please refer to [rg-db-group wiki](https://github.com/Billingegroup/rg-db-group/wiki/Set-up-regolith-and-databases)."),
            ("Email coauthors", "Send an email to coauthors letting them know the arXiv citation information."),
            ("Ask Simon if anything unfinished", "Ask Simon about any items unfinished."),
            ("Email Simon", "Email Simon if finish the above."),
        ]

        resubmission_checklist = [
            ("Work on the changes", "Make changes to the manuscript in the repo. You don't need to save it to a new name or anything because we can recover the old version by checking out the tagged version."),
            ("Write rebuttal letter", "Write a proper rebuttal letter based on reviewers' comments and place in the repo. In this letter address all of the referee's points, one by one. Place a copy of the referee's comments in the repo. Give it a unique filename in case there are more referee comments from later submissions!"),
            ("Check author list", "This is a good time to check that the author list is correct (don't need to add anyone or remove anyone) and that the acknowledgements have been done correctly, the figures are correct, the figure captions and table captions are correct and all the figures and tables are correctly referenced, and there are no compilation errors. Check all references for errors and update any 'unpublished' references if they have been published."),
            ("Diff the changes", "create a diff.pdf file that shows changes to the manuscript between the version in the tag of the previous submission and the current version, and include this in the resubmission."),
            ("Send to coauthors", "Send the final version to your coauthors. Tell them you will 'submit on' where is somewhere around 48 hours later and ask for any final corrections etc. from them. Offer them the chance to extend the deadline if they need more time, i.e., write 'if you need more time, lease let me know.' However, it is assumed that all the authors have been involved in the correction process up to this point so they only have to give it one final thought..."),
            ("Git commit changes", "Commit all the changes to your local repo, then push the changes to gitlab."),
            ("Resubmit", "Resubmit following the instructions of the journal."),
            ("Commit any additional changes", "If during the submission process you need to make any changes, do it in your local repo and make another commit and push."),
            ("Push a resubmission tag", "Make a new resubmission tag (see above for details)"),
            ("Check db entry", "Check the entry in citations.yml doesn't need to be updated, and update if it does."),
            ("Ask Simon if anything unfinished", "Ask Simon about any items unfinished."),
            ("Email Simon", "Email Simon if finish the above."),
        ]

        accepted_checklist = [
            ("Share the news", "Congratulations on the acceptance of the paper. Let all coauthors know the great news!"),
            ("Share with BNL if needed", "If it is a BNL paper (check with Simon, but it should acknowledge BNL funding-not just beamtime), send a pdf copy of the accepted version of the paper from the repo to Arlene at BNL to get a BNL publication number.  If you are not sure what this means, ask Simon"),
            ("Share the proof", "When you receive the proofs, share them quickly with all the authors. Request comments back in 24 hours. Proofs should be responded to within 48 hours in normal circumstances."),
            ("Respond the editor", "Go through and answer any questions from the editor."),
            ("Check author names", "Last chance to check that all the authors' names are correct and there are no missing authors."),
            ("Check institutions", "Check all authors' institutions are correct."),
            ("Check acknowledgement", "Make sure that all funding and all beamlines used are correctly acknowledged. Usually this is done by the bosses, but more eyes catch more mistakes."),
            ("Update db entry", "In citations.yml, (the reference should have been added during the submission step) double check the grants{}, facilities{}, nb{} field entries. Any questions, ask Simon. Put 'to be published' in the note{} section. If it has not been submitted to arxiv before, move the entry from rg-db-group to rg-db-public github repo. Otherwise, it should be at rg-db-public already. Create a PR to merge to the billingeGroup repository for edits if necessary."),
            ("Check db errors", "In your rg-db-public/local directory, run `regolith build publist --people lyang` (replace lyang with your name) to make sure that you publist is building properly. Make sure that the publication appears correctly with no errors and fix anything. If there are problems with the latex building, run the commands with --no-pdf, which yields the latex source but doesn't build it, then build the latex manually. If any problem about installing regolith and databases, please refer to [rg-db-group wiki](https://github.com/Billingegroup/rg-db-group/wiki/Set-up-regolith-and-databases)."),
            ("Check figures and tables", "Are all the figures, tables in the paper correct (the ones you intended)?"),
            ("Check the figure caption", "Check the Figure captions for errors. If they refer to a green line, is the relevant line green, and so on."),
            ("Check figure axis labels", "Check that the figure axis labels are correctly labeled. Make sure it doesn't say G when F is plotted. Make sure the units are correct. Make sure it says 'G (A^-2)' and NOT 'G(r)' (common mistake)"),
            ("Check table captions", "Check the table caption is correct. Are all the items in the table properly defined in the caption. If it is a crystal structure, are the space group and special positions mentioned in the caption? Is all the info correct?"),
            ("Check numbers in the table", "Check all the numbers in the tables for errors."),
            ("Check figure references", "Check references to the all figures and tables. Does reference to Figure 4 refer to the right figure for example"),
            ("Check references", "Go through the references and find all the errors. Correct errors in the bibliographic database AS WELL AS on the proofs the manuscript. Did all the journal names compile correctly? Are they all consistently in abbreviated form (or full form if that is the style, though that is rare). Volume, year and page numbers appear for all references? Hard to find errors in these numbers, but when you do, definitely correct the database!"),
            ("Check unpublished references", "If any references are listed as unpublished, on arXiv or submitted or something, check if they have appeared and give the full reference if at all possible. To do this, update the bibliographic database (e.g., citations.yml) with this information and then recompile the references, then copy paste the new bbl file back into the TeX source."),
            ("Check reference titles if needed", "If the manuscript style has titles in the references, make sure there are no capitalization or other compilation errors. Again, correct these in the database using {braces} around words where you want to preserve the capitalization as well as on the proof."),
            ("Read the paper", "Finally, after you have done all these 'mechanical' checks, read through the paper and try and find any typos or other problems. Resist the temptation to do any rewriting here...you are looking for mispellings and missing or extra words and so on."),
            ("Apply corrections from coauthors", "Collect all the corrections from the other authors and add any additional ones to the proof and return it."),
            ("Email coauthors", "Send an email to your coauthors that this was successfully resubmitted."),
            ("Revisit talk slides", "Revisit the set of talk slides that summarize the result in a few slides if they need to be updated. Iterate with Simon to convergence."),
            ("Revisit the highlight slide", "Create a single 'highlight' slide that describes the result following NSF/DOE guidelines. Place it in the 'highlight' folder. Iterate with Simon to convergence (highlight templates and examples can be found in http://gitlab.thebillingegroup.com/highlights/highlightTemplate)"),
            ("Create web news", "Create a web news story for thebillingegroup.com site. Place it in the 'highlight' folder. Iterate with Simon to convergence"),
            ("Revisit kudos", "Revisit the Kudos summary if it needs to be updated. Iterate with Simon to convergence."),
            ("Ask Simon if anything unfinished", "Ask Simon about any items unfinished."),
            ("Email Simon", "Email Simon if finish the above."),
        ]

        published_checklist = [
            ("Congrats", "Phew, it is over! Pat yourself on the back and celebrate!"),
            ("Let coauthors know", "Let your coauthors know the link to the final paper and the final reference."),
            ("Update db entry", "Update citations.yml at rg-db-public github repo with the correct reference information. Commit your edited citations.yml and create a PR to merge to the billingeGroup repository."),
            ("Check db entry", "CAREFULLY double and triple check the meta-data associated with the paper in citations.yml:"),
            ("Check grants in the db entry", "grant{} lists just the billinge-group grants that appeared in the acknowledgement section. They have standard abbreviations that are listed at the top of the citations.yml file, e.g., fwp, EFRC10, etc.. Use the right standard or the whole system becomes broken! If not sure.....ask Simon. List all grants in a comma-separated list."),
            ("Check the facility in the db entry", "facility{} is every beamline that was used for data collection. Again, use the standard abbreviations at the top of the file. Use two levels of granularity for each, so X17A would be: 'nsls, x17a', if X17A and X7B were used it would be 'nsls, x17a, x7b' and so on."),
            ("Check the nb in the db entry", "nb{} is some other tags, also listed at the top of the file. 'art' for a regular article and 'hilite' if it is one of our top top papers are the most common."),
            ("Check db errors", "In your rg-db-public/local directory, run `regolith build publist --people lyang` (replace lyang with your name) to make sure that you publist is building properly. Make sure that the publication appears correctly with no errors and fix anything. If there are problems with the latex building, run the commands with --no-pdf, which yields the latex source but doesn't build it, then build the latex manually."),
            ("Add/update to Zotero", "Add or update the published reference to the billinge-group-bib folder in our group Zotero account"),
            ("Finalize the highlight slide", "Make a highlight of your work and put it in gitlab/highlights (if not done already during the accepted paper checklist). Look in there for standards to work from. This is an important activity. Now you have done your great work, this is how you can advertise it to others. Top papers we send these highlights to the funding agencies.  Iterate the highlight with Simon till it is converged."),
            ("Finalize figures and talk slides", "Make figures and talk slides that will be used in talks and place these on gitlab on talks/figures.  Iterate this with Simon till it is converged."),
            ("Update arXiv if necessary", "If the paper was listed on a preprint server like arXiv, submit a note to arXiv that the paper has appeared and give the full reference. If the journal copyright allows you can post the published version here, but normally that is not alllowed! Still, it is important that people who find the paper on arXiv get directed to the correct reference."),
            ("Ask Simon if anything unfinished", "Ask Simon about any items unfinished."),
            ("Email Simon", "Email Simon if finish the above."),
        ]

        checklistm_list = []
        checklist_delay_days = [7]*len(presubmission_checklist) + [14]*len(submission_checklist) + [74]*len(resubmission_checklist) + [134]*len(accepted_checklist) + [194]*len(published_checklist)
        checklist_names = ["presubmission"]*len(presubmission_checklist) + ["submission"]*len(submission_checklist) + ["resubmission"]*len(resubmission_checklist) + ["accepted"]*len(accepted_checklist) + ["published"]*len(published_checklist)
        checklists = presubmission_checklist + submission_checklist + accepted_checklist + published_checklist
        for (name, objective), checklist_name, delay_days in zip(checklists, checklist_names, checklist_delay_days):
            checklistm = {'due_date': now + relativedelta(days=delay_days),
                       'name': f"{checklist_name} - {name}",
                       'objective': objective,
                       'audience': [],
                       'notes': [],
                       'status': 'converged',
                       'type': 'pr'
                       }
            checklistm_list.append(checklistm)

        pdoc.update({"milestones": checklistm_list})

        # update the deliverable to fit checklist prum
        pdoc.update({"deliverable": {
            "due_date": now + relativedelta(days=checklist_delay_days[-1]),
            "audience": ["simon"],
            "success_def": "audience is happy",
            "scope": [
                "checklist",
                "All publication data and metadata are correct and complete"],
            "platform": "regolith publication collection in rg-db-public",
            "roll_out": [
                "simon merging PRs"],
            "status": "converged"}
        })

        # update the kickoff to fit checklist prum
        pdoc.update({"kickoff": {
            "due_date": now,
            "audience": ["lead", "pi", "group_members"],
            "name": "Kick off meeting",
            "objective": "introduce project to the lead",
            "status": "finished"
        }})
        return pdoc

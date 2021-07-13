import os
from pathlib import Path
import pytest
import copy

from regolith.main import main

dash = "-"
helper_map = [
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre", "--status", "downloaded", "--title", "A flat world theory"],
     "A. Einstein proposal has been added/updated in proposal reviews\n"),
    (["helper", "a_manurev", "Einstein", "2020-09-15", "Nature", "On the Quantum Theory of Radiation",
      "--requester", "Niels Bohr", "--reviewer", "zcliu", "--status", "submitted", "--submitted_date", "2019-01-01"],
     "Einstein manuscript has been added/updated in manuscript reviews\n"),
    (["helper", "a_grppub_readlist", "test the lister", "pdf",
      "--title", "A list to test the lister", "--purpose", "Test the lister", "--date", "2021-04-01"],
     "test_the_lister has been added/updated in reading_lists\n"),
    (["helper", "a_projectum", "New projectum", "lyang",
      "--date", "2020-04-29", "--collaborators", "afriend", "--description", "more work",
      "--group_members", "ascopatz", "--grants", "SymPy-1.1", "--due_date", "2021-01-01"],
     "ly_newprojectum has been added in projecta\n"),
    (["helper", "a_proposal", "a new proposal", "100.0", "To destroy numbers",
      "--begin_date", "2020-09-15", "--end_date", "2022-02-14", "--duration", "16.89",
      "--authors", "Kurt Godel", "MC Escher", "Johann Sebastian Bach", "--currency", "Bitcoin",
      "--other_agencies", "Flatland", "--notes", "this is a sample added proposal", "--date", "2020-08-01"],
     "20_anewproposal has been added in proposals\n"),
    (["helper", "a_expense", "timbuktoo", "travel to timbuktoo", "--amount", "159.18",
      "--grants", "mrsec14", "dmref15", "--payee", "ashaaban",
      "--where", "bank", "--begin_date", "2020-06-20", "--end_date", "2020-06-25"],
     "2006as_timbuktoo has been added in expenses\n"),
    (["helper", "a_presentation", "flat earth", "Mars", "2020-06-26", "2020-06-26",
      "--type", "contributed_oral", "--person", "ashaaban", "--grants", "mrsec14",
      "--authors", "sbillinge", "ashaaban", "--abstract", "the earth is round as seen from mars",
      "--title", "On the roundness of the Earth", "--status", "in-prep",
      "--notes", "this is a sample added presentation"],
     "2006as_mars has been added in presentations\n2006as_mars has been added in expenses\n"),
    (["helper", "l_progress", "-l", "ascopatz"],
     "*************************[Started Projecta]**************************\n"
      "sb_firstprojectum\n"
      "    status: started, begin_date: 2020-04-28, due_date: 2021-05-05\n"
      "    description: My first projectum\n"
     ),
    (["helper", "l_progress", "-v", "-l", "ascopatz"],
     "*************************[Started Projecta]**************************\n"
      "sb_firstprojectum\n"
      "    status: started, begin_date: 2020-04-28, due_date: 2021-05-05\n"
      "    description: My first projectum\n"
      "    log_url: https://docs.google.com/document/d/1YC_wtW5Q\n"
      "    team:\n"
      "        group_members: ascopatz\n"
      "        collaborators: aeinstein, pdirac\n"
      "    deliverable:\n"
      "        audience: beginning grad in chemistry\n"
      "        scope: 1. UCs that are supported or some other scope description if it is software\n"
      "               2. sketch of science story if it is paper\n"
      "        platform: description of how and where the audience will access the deliverable.  Journal if it is a paper\n"
      "    milestones:\n"
      "        2020-05-20: Project lead presentation\n"
      "            objective: lead presents background reading and initial project plan\n"
      "            status: proposed\n"
      "        2020-05-27: planning meeting\n"
      "            objective: develop a detailed plan with dates\n"
      "            status: proposed\n"
     ),
    (["helper", "l_milestones", "--verbose"],
     "2021-05-05: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n2021-05-03: lead: abeing, ab_inactive, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n2021-01-01: lead: lyang, ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-27: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n2020-05-20: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-20: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n2020-05-06: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_milestones", "--verbose", "--current"],
     "2021-05-05: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n2021-05-03: lead: abeing, ab_inactive, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n2021-01-01: lead: lyang, ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-27: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n2020-05-20: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-20: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n2020-05-06: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_milestones", "--verbose", "--current", "--by_prum"],
     f"{dash*50}\n2021-05-03: lead: abeing, ab_inactive, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n{dash*50}\n2021-01-01: lead: lyang, ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n{dash*50}\n2021-05-05: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n2020-05-27: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n2020-05-20: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n"
     ),
    (["helper", "l_milestones", "--verbose", "--all"],
     "2021-05-05: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n2021-05-03: lead: abeing, ab_inactive, status: backburner\n    Type: meeting\n    Title: Kickoff\n    log url: None\n    Purpose: None\n    Audience: \n2021-05-03: lead: abeing, ab_inactive, status: paused\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n2021-05-03: lead: abeing, ab_inactive, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n2021-01-01: lead: lyang, ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-27: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n2020-05-20: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-20: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n2020-05-06: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n"
     ),
    (["helper", "l_milestones", "--verbose", "--person", "aeinstein"],
     "2021-05-05: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n2020-05-27: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n2020-05-20: lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n"
     ),
    (["helper", "l_milestones", "--verbose", "--stati", "finished"],
     "2020-05-06: lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n"
     ),
    (["helper", "l_milestones", "--verbose", "--finished"],
     "2020-05-06: lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n"
     ),
    (["helper", "l_milestones", "--verbose", "--lead", "lyang"],
     "2021-01-01: lead: lyang, ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_projecta", "--verbose", "--orphan"],
     "ab_inactive\n    status: started, begin_date: None, due_date: None, end_date: None, grant: None\n    description: None\n    team:\n        lead: abeing\n        group_members: None\n        collaborators: None\n"
     ),
    (["helper", "l_projecta", "--verbose", "--lead", "ascopatz"],
     "sb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_projecta", "--verbose", "--person", "ascopatz"],
     "ly_newprojectum\n    status: started, begin_date: 2020-04-29, due_date: None, end_date: None, grant: SymPy-1.1\n    description: more work\n    team:\n        lead: lyang\n        group_members: ascopatz\n        collaborators: afriend\nsb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_projecta", "--grant", "SymPy-1.1"],
     "ly_newprojectum\nsb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--grp_by_lead"],
     "abeing:\n    ab_inactive\nlyang:\n    ly_newprojectum\nascopatz:\n    sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--all"],
     "ab_inactive\nly_newprojectum\nsb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--current"],
     "ab_inactive\nly_newprojectum\nsb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--grp_by_lead", "-l", "ascopatz"],
     "ascopatz:\n    sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose"],
     "ab_inactive\n    status: started, begin_date: None, due_date: None, end_date: None, grant: None\n    description: None\n    team:\n        lead: abeing\n        group_members: None\n        collaborators: None\nly_newprojectum\n    status: started, begin_date: 2020-04-29, due_date: None, end_date: None, grant: SymPy-1.1\n    description: more work\n    team:\n        lead: lyang\n        group_members: ascopatz\n        collaborators: afriend\nsb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: None, end_date: 2020-06-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_projecta", "--ended", "--date", "2020-06-02"],
     "\nNo projecta finished within the 7 days leading up to 2020-06-02\n"
     ),
    (["helper", "l_grants", "--current", "--date", "2020-05-25"],
     "sym2.0, awardnr: , acctn: , 2019-06-01 to 2030-12-31\n"
     ),
    (["helper", "l_members", "--current", "-v"],
     "    -- Assistant Scientists --\n"
     "Simon J. L. Billinge, professor\n"
     "    email: sb2896@columbia.edu | group_id: sbillinge\n"
     "    github_id: None | orcid: 0000-0002-9432-4248\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
     ),
    (["helper", "l_members", "-v"],
     "    -- Assistant Scientists --\n"
     "Simon J. L. Billinge, professor\n"
     "    email: sb2896@columbia.edu | group_id: sbillinge\n"
     "    github_id: None | orcid: 0000-0002-9432-4248\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
     "Anthony Scopatz, professor\n"
     "    email: scopatz@cec.sc.edu | group_id: scopatz\n"
     "    github_id: ascopatz | orcid: 0000-0002-9432-4248\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
     "    -- Undergrads --\n"
     "Abstract Being, intern\n"
     "    email: None | group_id: abeing\n"
     "    github_id: None | orcid: None\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
     ),
    (["helper", "l_members", "--prior", "-v"],
     "    -- Assistant Scientists --\n"
     "Anthony Scopatz, professor\n"
     "    email: scopatz@cec.sc.edu | group_id: scopatz\n"
     "    github_id: ascopatz | orcid: 0000-0002-9432-4248\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
     "    -- Undergrads --\n"
     "Abstract Being, intern\n"
     "    email: None | group_id: abeing\n"
     "    github_id: None | orcid: None\n"
     "    current organization: The University of South Carolina\n"
     "    current position: Assistant Professor\n"
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
    (["helper", "l_abstract", "--title", "graphitic"],
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--loc_inst", "upton"],
     "---------------------------------------\n"
     "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract",  "--year", "2018"],
     "---------------------------------------\n"
     "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We made the case for local structure\n"
     "---------------------------------------\n"
     "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--author", "scopatz"],
     "---------------------------------------\n"
     "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We made the case for local structure\n"
     "---------------------------------------\n"
     "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--loc_inst", "upton", "--year", "2018"],
     "---------------------------------------\n"
     "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--author", "scopatz", "--loc_inst", "upton"],
     "---------------------------------------\n"
     "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n"
     "\nAnthony Scopatz\n"
     "\nAbstract: We pulled apart graphite with tape\n"
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--author", "scopatz", "--year", "2018", "--loc_inst", "upton", "--title", "graphitic"],
     "---------------------------------------\n"
     "Title: Graphitic Dephenestration\n\n"
     "Anthony Scopatz, Anthony B Friend\n\n"
     "Abstract: We pulled apart graphite with tape\n"
     ),
    (["helper", "l_abstract", "--loc_inst", "columbiau"],
     "---------------------------------------\n"
     "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
     "Anthony Scopatz\n\n"
     "Abstract: We made the case for local structure\n"
     ),
    (["helper", "u_milestone", "sb_firstprojectum", "--index", "5",
      "--status", "converged", "--due_date", "2020-06-01", "--notes", "do this",
      "do that"],
     "sb_firstprojectum has been updated in projecta\n"
     ),
    (["helper", "u_milestone", "sb"],
     "Projecta not found. Projecta with similar names: \n"
     "sb_firstprojectum\n"
     "Please rerun the helper specifying the complete ID.\n"
     ),
    (["helper", "u_milestone", "sb_firstprojectum"],
     "Please choose from one of the following to update/add:\n"
     "1. new milestone\n"
     "2. Kick off meeting    due date: 2020-05-06    status: finished\n"
     "3. Project lead presentation    due date: 2020-05-20    status: proposed\n"
     "4. planning meeting    due date: 2020-05-27    status: proposed\n"
     "5. deliverable    due date: 2020-06-01    status: converged\n"
     ),
    (["helper", "u_milestone", "sb_firstprojectum", "--verbose"],
     "Please choose from one of the following to update/add:\n"
     "1. new milestone\n"
     "2. Kick off meeting    due date: 2020-05-06    status: finished\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objective: introduce project to the lead\n"
     "     notes:\n"
     "       - kickoff note\n"
     "3. Project lead presentation    due date: 2020-05-20    status: proposed\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objective: lead presents background reading and initial project plan\n"
     "     type: meeting\n"
     "     notes:\n"
     "       - do background reading\n"
     "       - understand math\n"
     "4. planning meeting    due date: 2020-05-27    status: proposed\n"
     "     audience: ['lead', 'pi', 'group_members']\n"
     "     objective: develop a detailed plan with dates\n"
     "     type: mergedpr\n"
     "5. deliverable    due date: 2020-06-01    status: converged\n"
     "     audience: ['beginning grad in chemistry']\n"
     "     notes:\n"
     "       - deliverable note\n"
     "       - do this\n"
     "       - do that\n"
     ),
    (["helper", "u_milestone", "sb_firstprojectum", "--current"],
     "Please choose from one of the following to update/add:\n"
     "1. new milestone\n"
     "3. Project lead presentation    due date: 2020-05-20    status: proposed\n"
     "4. planning meeting    due date: 2020-05-27    status: proposed\n"
     "5. deliverable    due date: 2020-06-01    status: converged\n"
     ),
    (["helper", "u_logurl", "sb", "--index", "1", "https://docs.google.com/document/d/1pQMFpuI"],
     "sb_firstprojectum has been updated with a log_url of https://docs.google.com/document/d/1pQMFpuI\n"
     ),
    (["helper", "u_logurl", "ly", "https://docs.google.com/document/d/1pQMFpuI"],
     "There does not seem to be a projectum with this exact name in this database.\n"
     "However, there are projecta with similar names: \n"
     "1. ly_newprojectum     current url: \n"
     "Please rerun the u_logurl helper with the same name as previously inputted, "
     "but with the addition of -i followed by a number corresponding to one of the "
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
    (["helper", "l_todo", "--short", "65",
      "--date", "2020-07-13", "--assigned_by", "scopatz", "--assigned_to",
      "sbillinge"],
     "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
     "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
     "--------------------------------------------------------------------------------\n"
     "started:\n"
     "(1) read paper (6|2|60.0|reading,downtime|scopatz)\n"
     "------------------------------\n"
     "Tasks (decreasing priority going up)\n"
     "------------------------------\n"
     "2020-07-19(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz)\n"
     "------------------------------\n"
     "Deadlines:\n"
     "------------------------------\n"
     ),
    (["helper", "l_todo", "--tags", "downtime", "--date", "2020-07-13",
      "--assigned_by",
      "sbillinge", "--assigned_to", "sbillinge"],
     "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
     "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
     "--------------------------------------------------------------------------------\n"
     "started:\n"
     "(2) prepare the presentation (16|0|30.0|downtime|sbillinge)\n"
     "     - about 10 minutes\n"
     "     - don't forget to upload to the website\n"
     "------------------------------\n"
     "Tasks (decreasing priority going up)\n"
     "------------------------------\n"
     "------------------------------\n"
     "Deadlines:\n"
     "------------------------------\n"
     ),
    (["helper", "l_todo", "--assigned_to", "wrong_id"],
     "The id you entered can't be found in todos.yml.\n"
     ),
    (
        ["helper", "a_todo", "test a_todo", "6", "50", "--assigned_to",
         "sbillinge",
         "--assigned_by", "sbillinge", "--begin_date", "2020-07-06",
         "--importance",
         "2", "--deadline", "--notes", "test notes 1", "test notes 2", "--tags",
         "tag1",
         "tag2",
         "--date", "2020-07-10"],
        "The task \"test a_todo\" for sbillinge has been added in todos collection.\n"
    ),
    (["helper", "f_todo", "--index", "3", "--assigned_to", "sbillinge",
      "--end_date", "2020-07-20", "--date", "2020-07-13"],
     "The task \"(3) test a_todo\" in test for sbillinge has been marked as finished.\n"
     ),
    (["helper", "f_todo", "--assigned_to", "sbillinge", "--date",
      "2020-07-13"],
     "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
     "Please choose from one of the following to update:\n"
     "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
     "--------------------------------------------------------------------------------\n"
     "started:\n"
     "(2) prepare the presentation (16|0|30.0|downtime|sbillinge)\n"
     "     - about 10 minutes\n"
     "     - don't forget to upload to the website\n"
     "(1) read paper (6|2|60.0|reading,downtime|scopatz)\n"
     "------------------------------\n"
     "Tasks (decreasing priority going up)\n"
     "------------------------------\n"
     "2020-07-19(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz)\n"
     "------------------------------\n"
     "Deadlines:\n"
     "------------------------------\n"
     ),
    (["helper", "u_todo", "--index", "3", "--assigned_to", "sbillinge",
      "--description", "update the description", "--due_date", "2020-07-06",
      "--estimated_duration", "35", "--importance", "2", "--status", "finished",
      "--notes", "some new notes", "notes2", "--tags", "newtag1", "newtag2",
      "--begin_date", "2020-06-06", "--deadline", "t",
      "--end_date", "2020-07-07", "--date", "2020-07-13"],
     "The task \"(3) test a_todo\" in test for sbillinge has been updated.\n"
     ),
    (["helper", "u_todo", "--assigned_to", "sbillinge", "--stati", "started",
      "finished", "--filter", "description", "the", "--date",
      "2020-07-13"],
     "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
     "Please choose from one of the following to update:\n"
     "(index) action (days to due date|importance|expected duration (mins)|assigned by)\n"
     "--------------------------------------------------------------------------------\n"
     "started:\n"
     "(2) prepare the presentation (16|0|30.0|downtime|sbillinge)\n"
     "     - about 10 minutes\n"
     "     - don't forget to upload to the website\n"
     "finished:\n"
     "(3) update the description (-7|2|35.0|tag1,tag2,newtag1,newtag2|sbillinge)\n"
     "     - test notes 1\n"
     "     - test notes 2\n"
     "     - some new notes\n"
     "     - notes2\n"
     "------------------------------\n"
     "Tasks (decreasing priority going up)\n"
     "------------------------------\n"
     "2020-07-06(-7 days): (3) update the description (-7|2|35.0|tag1,tag2,newtag1,newtag2|sbillinge)\n"
     "     - test notes 1\n"
     "     - test notes 2\n"
     "     - some new notes\n"
     "     - notes2\n"
     "------------------------------\n"
     "Deadlines:\n"
     "------------------------------\n"
     ),
    (["helper", "f_prum", "sb_firstprojectum", "--end_date", "2020-07-01"],
     "sb_firstprojectum status has been updated to finished\n"
     ),
    (["helper", "f_prum", "sb_"],
     "Projectum not found. Projecta with similar names: \n"
     "sb_firstprojectum     status:finished\n"
     "Please rerun the helper specifying the complete ID.\n"
     ),
    (["helper", "lister", "people"],
     "Results of your search:\nabeing    \nsbillinge    \nscopatz\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon"],
     "Results of your search:\n"
     "sbillinge\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon", "--return_fields", "name", "position"],
     "Results of your search:\nsbillinge    name: Simon J. L. Billinge    position: professor\n"),
    (["helper", "lister", "people", "--keys"],
     "Available keys:\n"
     "['_id', 'active', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
     "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
     "'github_id', 'google_scholar_url', 'grp_mtg_active', 'hindex', "
     "'home_address', 'initials', 'linkedin_url', "
     "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
     "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
     "'title']\n"),
    (["helper", "lister", "people", "--kv_filter", "name", "simon", "--keys"],
     "Results of your search:\nsbillinge\n"
     "Available keys:\n"
     "['_id', 'active', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
     "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
     "'github_id', 'google_scholar_url', 'grp_mtg_active', 'hindex', "
     "'home_address', 'initials', 'linkedin_url', "
     "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
     "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
     "'title']\n"
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
    (["helper", "makeappointments", "run", "--no-gui", "--projection-from-date", "2020-08-31"],
      "WARNING: appointment gap for scopatz from 2019-09-01 to 2019-12-31\n"
     "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
     "appointments on outdated grants:\n"
     "    person: scopatz, appointment: f19, grant: dmref15,\n"
     "            from 2019-05-02 until 2019-09-01\n"
     "    person: scopatz, appointment: s20, grant: sym,\n"
     "            from 2020-01-01 until 2020-05-15\n"
     "appointments on depleted grants:\n"
     "    person: scopatz, appointment: ss20, grant: abc42,\n"
     "            from 2020-07-15 until 2020-08-31\n"
     "    person: scopatz, appointment: ss21, grant: future_grant,\n"
     "            from 2020-09-06 until 2021-08-31\n"
     "underspent grants:\n"
     "    dmref15: end: 2019-05-01\n"
     "      projected underspend: 56.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: -3.5\n"
     "    sym: end: 2030-12-31\n"
     "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: 0.06\n"
     "cumulative underspend = 64.0 months, cumulative months to support = 0\n"
     "overspent grants:\n"
     "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n"
     "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
     "plotting mode is on\n"
     ),
    (["helper", "makeappointments", "run", "--no-gui", "--projection-from-date", "2020-08-31", "-v"],
     "skipping ta since it is in the blacklist\n"
     "WARNING: appointment gap for scopatz from 2019-09-01 to 2019-12-31\n"
     "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
     "skipping sym2.0 since it it does not support any appointments\n"
     "appointments on outdated grants:\n"
     "    person: scopatz, appointment: f19, grant: dmref15,\n"
     "            from 2019-05-02 until 2019-09-01\n"
     "    person: scopatz, appointment: s20, grant: sym,\n"
     "            from 2020-01-01 until 2020-05-15\n"
     "appointments on depleted grants:\n"
     "    person: scopatz, appointment: ss20, grant: abc42,\n"
     "            from 2020-07-15 until 2020-08-31\n"
     "    person: scopatz, appointment: ss21, grant: future_grant,\n"
     "            from 2020-09-06 until 2021-08-31\n"
     "underspent grants:\n"
     "    dmref15: end: 2019-05-01\n"
     "      projected underspend: 56.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: -3.5\n"
     "    sym: end: 2030-12-31\n"
     "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: 0.06\n"
     "cumulative underspend = 64.0 months, cumulative months to support = 0\n"
     "overspent grants:\n"
     "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n"
     "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
     "plotting mode is on\n"
     ),
    (["helper", "makeappointments", "run", "--no-plot", "--projection-from-date", "2020-08-31"],
     "WARNING: appointment gap for scopatz from 2019-09-01 to 2019-12-31\n"
     "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
     "appointments on outdated grants:\n"
     "    person: scopatz, appointment: f19, grant: dmref15,\n"
     "            from 2019-05-02 until 2019-09-01\n"
     "    person: scopatz, appointment: s20, grant: sym,\n"
     "            from 2020-01-01 until 2020-05-15\n"
     "appointments on depleted grants:\n"
     "    person: scopatz, appointment: ss20, grant: abc42,\n"
     "            from 2020-07-15 until 2020-08-31\n"
     "    person: scopatz, appointment: ss21, grant: future_grant,\n"
     "            from 2020-09-06 until 2021-08-31\n"
     "underspent grants:\n"
     "    dmref15: end: 2019-05-01\n"
     "      projected underspend: 56.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: -3.5\n"
     "    sym: end: 2030-12-31\n"
     "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
     "      required ss+gra burn: 0.06\n"
     "cumulative underspend = 64.0 months, cumulative months to support = 0\n"
     "overspent grants:\n"
     "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n"
     "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
     ),
    (["helper", "v_meetings", "--test"], "Meeting validator helper\n")
]

db_srcs = [
    # "mongo",
    "fs"
]


@pytest.mark.parametrize("db_src", db_srcs)
@pytest.mark.parametrize("hm", helper_map)
def test_helper_python(hm, make_db, db_src, make_mongodb, capsys):
    testfile = Path(__file__)

    if db_src == "fs":
        repo = Path(make_db)
    elif db_src == "mongo":
        if make_mongodb is False:
            pytest.skip("Mongoclient failed to start")
        else:
            repo = Path(make_mongodb)
    os.chdir(repo)

    main(args=hm[0])
    out, err = capsys.readouterr()
    assert out == hm[1]

    expecteddir = testfile.parent / "outputs" / hm[0][1]

    if expecteddir.is_dir():
        if db_src == "fs":
            test_dir = repo / "db"
            assert_outputs(test_dir, expecteddir)
        elif db_src == "mongo":
            from regolith.database import connect
            from regolith.runcontrol import DEFAULT_RC, load_rcfile
            os.chdir(repo)
            rc = copy.copy(DEFAULT_RC)
            rc._update(load_rcfile("regolithrc.json"))
            with connect(rc) as client:
                mongo_database = client[rc.databases[0]['name']]
                assert_mongo_vs_yaml_outputs(expecteddir, mongo_database)

helper_map_loose = [
    (["helper", "l_abstract"],
     "-------------------------------------------\n"
     "please rerun specifying at least one filter\n"
     "-------------------------------------------\n"
     )
    ]
@pytest.mark.parametrize("hm", helper_map_loose)
def test_helper_python_loose(hm, make_db, capsys):
    repo = Path(make_db)
    testfile = Path(__file__)
    os.chdir(repo)

    main(args=hm[0])
    out, err = capsys.readouterr()
    assert hm[1] in out

def assert_mongo_vs_yaml_outputs(expecteddir, mongo_database):
    from regolith.mongoclient import load_mongo_col
    from regolith.fsclient import load_yaml
    from regolith.dates import convert_doc_iso_to_date
    os.chdir(expecteddir)
    for root, dirs, files in os.walk("."):
        for file in files:
            fn2 = expecteddir / root / file
            expected_collection_dict = load_yaml(fn2)
            base, ext = os.path.splitext(file)
            mongo_coll_pointer = mongo_database[base]
            edited_collection_dict = load_mongo_col(mongo_coll_pointer)
            for k, v in edited_collection_dict.items():
                edited_collection_dict[k] = convert_doc_iso_to_date(v)
            for k, v in expected_collection_dict.items():
                expected_collection_dict[k] = convert_doc_iso_to_date(v)
            assert edited_collection_dict == expected_collection_dict


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

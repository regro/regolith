import copy
import os
from pathlib import Path

import pytest
import requests_mock

from regolith.main import main
from regolith.schemas import alloweds

MILESTONE_TYPES = alloweds.get("MILESTONE_TYPES")

dash = "-"
helper_map = [
    (
        ["helper", "attestations", "--grant", "dmref15", "--no-plot", "--verbose"],
        "Instructions/Notes:\n"
        "  Quarters are: Q1 July thru Sept, Q2 Oct - Dec, Q3 Jan - Mar, Q4 Apr - Jun\n"
        "  Grad salaries are about $3400 per month\n"
        "Collecting Appointments for grant dmref15:\n"
        "scopatz, from 2019-02-01 to 2019-03-31, loading 0.75. Total months: 1.43\n"
        "\n-----------\nLoadings by month\n------------\n"
        "2018-05-01:\n"
        "2018-06-01:\n"
        "2018-07-01:\n"
        "2018-08-01:\n"
        "2018-09-01:\n"
        "2018-10-01:\n"
        "2018-11-01:\n"
        "2018-12-01:\n"
        "2019-01-01:\n"
        "2019-02-01:\n"
        "    scopatz\tloading: 2550.0\n"
        "2019-03-01:\n"
        "    scopatz\tloading: 2550.0\n"
        "2019-04-01:\n"
        "2019-05-01:\n"
        "\n----------------\nExpenses\n----------------\n"
        "2018-01-10 (reimb date), 2018-01-10 (expense date): amount: 500, \n"
        "2019-02-15 (reimb date), 2018-01-10 (expense date): amount: 1000, \n"
        "  payee: scopatz purpose: testing the databallectionsse\n"
        "2018-05-01: expenses monthly total = 0.00\n"
        "2018-06-01: expenses monthly total = 0.00\n"
        "2018-07-01: expenses monthly total = 0.00\n"
        "2018-08-01: expenses monthly total = 0.00\n"
        "2018-09-01: expenses monthly total = 0.00\n"
        "2018-10-01: expenses monthly total = 0.00\n"
        "2018-11-01: expenses monthly total = 0.00\n"
        "2018-12-01: expenses monthly total = 0.00\n"
        "2019-01-01: expenses monthly total = 0.00\n"
        "2019-02-01: expenses monthly total = 1000.00\n"
        "2019-03-01: expenses monthly total = 0.00\n"
        "2019-04-01: expenses monthly total = 0.00\n"
        "2019-05-01: expenses monthly total = 0.00\n"
        "Total spend = 1500\n",
    ),
    (
        [
            "helper",
            "attestations",
            "--begin-date",
            "2019-01-01",
            "--end-date",
            "2019-05-30",
            "--effort-reporting",
            "--no-plot",
        ],
        ",, 2019-01-01, 2019-02-01, 2019-03-01, 2019-04-01, 2019-05-01\n"
        "scopatz, dmref15, 0.0, 75.0, 75.0, 0.0, 0.0\n",
    ),
    (
        ["helper", "l_progress", "-l", "pliu", "--date", "2022-01-09"],
        "\nProgress report for pliu, generated 2022-01-09\n"
        "*************************[Orphan Projecta]*************************\n"
        "pl_thirdprojectum, status: backburner\n"
        "*************************[Finished Projecta]*************************\n"
        "pl_firstprojectum, grant: None\n"
        "  None\n"
        "  finished: 2020-07-27\n"
        "*************************[Proposed Projecta]*************************\n"
        "pl_secondprojectum\n"
        "\n"
        "  description: None\n"
        "  milestones:\n"
        "  -------------\n"
        "    Milestone (milest, due: 2021-08-03, converged)\n"
        "      - None\n"
        "\n"
        "*************************[In Progress Projecta]*************************\n",
    ),
    (
        ["helper", "l_progress", "-l", "pliu", "--date", "2022-01-09"],
        "\nProgress report for pliu, generated 2022-01-09\n"
        "*************************[Orphan Projecta]*************************\n"
        "pl_thirdprojectum, status: backburner\n"
        "*************************[Finished Projecta]*************************\n"
        "pl_firstprojectum, grant: None\n"
        "  None\n"
        "  finished: 2020-07-27\n"
        "*************************[Proposed Projecta]*************************\n"
        "pl_secondprojectum\n"
        "\n"
        "  description: None\n"
        "  milestones:\n"
        "  -------------\n"
        "    Milestone (milest, due: 2021-08-03, converged)\n"
        "      - None\n"
        "\n"
        "*************************[In Progress Projecta]*************************\n",
    ),
    (
        ["helper", "l_progress", "-v", "-l", "ascopatz", "--date", "2022-01-09"],
        "\nProgress report for ascopatz, generated 2022-01-09\n"
        "*************************[Orphan Projecta]*************************\n"
        "*************************[Finished Projecta]*************************\n"
        "*************************[Proposed Projecta]*************************\n"
        "*************************[In Progress Projecta]*************************\n"
        "First Projectum\n"
        "  status: started, begin_date: 2020-04-28, due_date: 2021-05-05\n"
        "  My first projectum\n"
        "  log_url: https://docs.google.com/document/d/1YC_wtW5Q\n"
        "  team:\n"
        "    group_members: ascopatz\n"
        "    collaborators: aeinstein, pdirac\n"
        "  deliverable:\n"
        "    audience: beginning grad in chemistry\n"
        "    scope: 1. UCs that are supported or some other scope description if it "
        "is software\n"
        "           2. sketch of science story if it is paper\n"
        "    platform: description of how and where the audience will access the "
        "deliverable.  Journal if it is a paper\n"
        "  milestones:\n"
        "    2020-05-20: Project lead presentation\n"
        "      objective: lead presents background reading and initial project plan\n"
        "      status: started\n"
        "    2020-05-27: planning meeting\n"
        "      objective: develop a detailed plan with dates\n"
        "      status: proposed\n",
    ),
    (
        ["helper", "l_milestones", "--verbose"],
        "2021-08-03 (milest): lead: pliu, pl_secondprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl2\n"
        "2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n"
        "2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        "2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--current"],
        "2021-08-03 (milest): lead: pliu, pl_secondprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl2\n"
        "2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n"
        "2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        "2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--current", "--by-prum"],
        f"{dash * 50}\n"
        f"2021-08-03 (milest): lead: pliu, pl_secondprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl2\n"
        f"{dash * 50}\n"
        f"2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n"
        f"2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        f"2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--all"],
        "2021-08-26 (pl_fir): lead: pliu, pl_firstprojectum, status: finished\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: pl_firstprojectum\n2021-08-26 (pl_sec): lead: pliu, pl_secondprojectum, status: finished\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: pl_secondprojectum\n2021-08-26 (pl_thi): lead: pliu, pl_thirdprojectum, status: finished\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: pl_thirdprojectum\n2021-08-03 (kopl_f): lead: pliu, pl_firstprojectum, status: backburner\n    Type: meeting\n    Title: Kickoff\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: kopl_firstprojectum\n2021-08-03 (milest): lead: pliu, pl_firstprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl1\n2021-08-03 (kopl_s): lead: pliu, pl_secondprojectum, status: backburner\n    Type: meeting\n    Title: Kickoff\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: kopl_secondprojectum\n2021-08-03 (milest): lead: pliu, pl_secondprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl2\n2021-08-03 (kopl_t): lead: pliu, pl_thirdprojectum, status: backburner\n    Type: meeting\n    Title: Kickoff\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: kopl_thirdprojectum\n2021-08-03 (milest): lead: pliu, pl_thirdprojectum, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_pl3\n2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n2021-05-03 (koab_i): lead: abeing, ab_inactive, status: backburner\n    Type: meeting\n    Title: Kickoff\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: koab_inactive\n2021-05-03 (ab_ina): lead: abeing, ab_inactive, status: paused\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: ab_inactive\n2021-05-03 (milest): lead: abeing, ab_inactive, status: converged\n    Type: \n    Title: Milestone\n    log url: None\n    Purpose: None\n    Audience: \n    uuid: milestone_uuid_inactive\n"
        "2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        "2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n"
        "2020-05-06 (kosb_f): lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n    uuid: kosb_firstprojectum\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--person", "aeinstein"],
        "2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n"
        "2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        "2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--stati", "finished"],
        "2021-08-26 (pl_sec): lead: pliu, pl_secondprojectum, status: finished\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: pl_secondprojectum\n2020-05-06 (kosb_f): lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n    uuid: kosb_firstprojectum\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--finished"],
        "2021-08-26 (pl_sec): lead: pliu, pl_secondprojectum, status: finished\n    Type: \n    Title: deliverable\n    log url: None\n    Purpose: deliver\n    Audience: \n    uuid: pl_secondprojectum\n2020-05-06 (kosb_f): lead: ascopatz, sb_firstprojectum, status: finished\n    Type: meeting\n    Title: Kick off meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: introduce project to the lead\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - kickoff note\n    uuid: kosb_firstprojectum\n",
    ),
    (
        ["helper", "l_milestones", "--verbose", "--lead", "ascopatz"],
        "2021-05-05 (sb_fir): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: deliver\n    Audience: beginning grad in chemistry\n    Notes:\n      - deliverable note\n    uuid: sb_firstprojectum\n"
        "2020-05-27 (milest): lead: ascopatz, sb_firstprojectum, status: proposed\n    Type: mergedpr\n    Title: planning meeting\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: develop a detailed plan with dates\n    Audience: ascopatz, scopatz, ascopatz\n    uuid: milestone_uuid_sb1_2\n"
        "2020-05-20 (milest): lead: ascopatz, sb_firstprojectum, status: started\n    Type: meeting\n    Title: Project lead presentation\n    log url: https://docs.google.com/document/d/1YC_wtW5Q\n    Purpose: lead presents background reading and initial project plan\n    Audience: ascopatz, scopatz, ascopatz\n    Notes:\n      - do background reading\n      - understand math\n    uuid: milestone_uuid_sb1\n",
    ),
    (
        ["helper", "l_projecta", "--verbose", "--orphan"],
        "ab_inactive\n    status: backburner, begin_date: 2020-05-03, due_date: 2021-05-03, grant: dmref15\n    description: a prum that has various inactive states in milestones and overall\n    team:\n        lead: abeing\n        group_members: None\n        collaborators: None\n",
    ),
    (
        ["helper", "l_projecta", "--verbose", "--lead", "ascopatz"],
        "sb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: 2021-05-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n",
    ),
    (
        ["helper", "l_projecta", "--verbose", "--person", "ascopatz"],
        "sb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: 2021-05-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n",
    ),
    (["helper", "l_projecta", "--grant", "SymPy-1.1"], "sb_firstprojectum (started)\n"),
    (
        ["helper", "l_projecta", "--grp_by_lead"],
        "abeing:\n    ab_inactive (backburner)\npliu:\n    pl_firstprojectum (finished)\n    pl_secondprojectum (proposed)\n    pl_thirdprojectum (backburner)\nascopatz:\n    sb_firstprojectum (started)\n",
    ),
    (
        ["helper", "l_projecta", "--all"],
        "ab_inactive (backburner)\npl_firstprojectum (finished)\npl_secondprojectum (proposed)\npl_thirdprojectum (backburner)\nsb_firstprojectum (started)\n",
    ),
    (["helper", "l_projecta", "--current"], "pl_secondprojectum (proposed)\nsb_firstprojectum (started)\n"),
    (["helper", "l_projecta", "--grp_by_lead", "-l", "ascopatz"], "ascopatz:\n    sb_firstprojectum (started)\n"),
    (
        ["helper", "l_projecta", "--verbose"],
        "ab_inactive\n    status: backburner, begin_date: 2020-05-03, due_date: 2021-05-03, grant: dmref15\n    description: a prum that has various inactive states in milestones and overall\n    team:\n        lead: abeing\n        group_members: None\n        collaborators: None\n"
        "pl_firstprojectum\n    status: finished, begin_date: 2020-07-25, due_date: 2021-08-26, end_date: 2020-07-27, grant: None\n    description: None\n    team:\n        lead: pliu\n        group_members: None\n        collaborators: None\n"
        "pl_secondprojectum\n    status: proposed, begin_date: 2020-07-25, due_date: 2021-08-26, grant: None\n    description: None\n    team:\n        lead: pliu\n        group_members: None\n        collaborators: None\n"
        "pl_thirdprojectum\n    status: backburner, begin_date: 2020-07-25, due_date: 2021-08-26, grant: None\n    description: None\n    team:\n        lead: pliu\n        group_members: None\n        collaborators: None\n"
        "sb_firstprojectum\n    status: started, begin_date: 2020-04-28, due_date: 2021-05-05, grant: SymPy-1.1\n    description: My first projectum\n    team:\n        lead: ascopatz\n        group_members: ascopatz\n        collaborators: aeinstein, pdirac\n",
    ),
    (
        ["helper", "l_projecta", "--ended", "--date", "2020-06-02"],
        "\nNo projecta finished within the 7 days leading up to 2020-06-02\n",
    ),
    (
        ["helper", "l_grants", "--current", "--date", "2020-05-25"],
        "\nAdministered by: apam\n"
        "  sym2.0         \t awardnr: NF-1234        \t acctn: n/a                 \t 2019-06-01 to 2030-12-31\n",
    ),
    (
        ["helper", "l_grants", "--current", "--date", "2020-05-25", "--reveal-hidden"],
        "\nAdministered by: apam\n"
        "  sym2.0         \t awardnr: NF-1234        \t acctn: n/a                 \t 2019-06-01 to 2030-12-31\n",
    ),
    (
        ["helper", "l_grants", "--current", "--date", "2020-05-25", "--verbose"],
        "\nAdministered by: apam\n"
        "  sym2.0         \t awardnr: NF-1234        \t acctn: n/a                 \t 2019-06-01 to 2030-12-31\n"
        "      funds available: $2,100 on 2021-01-03\n",
    ),
    (
        ["helper", "l_members", "--current", "-v"],
        "    -- Assistant Scientists --\n"
        "Simon J. L. Billinge, professor\n"
        "    email: sb2896@columbia.edu | group_id: sbillinge\n"
        "    github_id: None | orcid: 0000-0002-9432-4248\n"
        "    current organization: The University of South Carolina\n"
        "    current position: Assistant Professor\n",
    ),
    (
        ["helper", "l_members", "-v"],
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
        "    current position: Assistant Professor\n",
    ),
    (
        ["helper", "l_members", "--prior", "-v"],
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
        "    current position: Assistant Professor\n",
    ),
    (["helper", "l_members", "--filter", "name", "sco"], "scopatz    \n"),
    (
        ["helper", "l_members", "--filter", "name", "sco", "-v"],
        "Anthony Scopatz, professor | group_id: scopatz\n"
        "    orcid: 0000-0002-9432-4248 | github_id: ascopatz\n",
    ),
    (
        [
            "helper",
            "l_contacts",
            "run",
            "--name",
            "ny",
            "--inst",
            "col",
            "--notes",
            "coffee",
            "--date",
            "2020-01-15",
            "--range",
            "2",
        ],
        "Anthony B Friend  |  afriend  |  institution: Columbia University  |  email: friend@deed.com\n",
    ),
    (
        [
            "helper",
            "l_contacts",
            "run",
            "--name",
            "ny",
            "--inst",
            "col",
            "--notes",
            "coffee",
            "--date",
            "2019-01-15",
            "--range",
            "2",
        ],
        "\n",
    ),
    (
        ["helper", "l_contacts", "run", "--verbose"],
        "Anthony B Friend\n"
        "    _id: afriend\n"
        "    email: friend@deed.com\n"
        "    institution: Columbia University\n"
        "    department: physics\n"
        "    notes:\n"
        "        -The guy I meet for coffee sometimes\n"
        "    aka:\n"
        "        -A. B. Friend\n        -AB Friend\n        -Tony Friend\n",
    ),
    (
        ["helper", "l_abstract", "--year", "2018", "--author", "afriend"],
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--year", "2018", "--title", "nanostructure"],
        "\n---------------------------------------\n"
        "2018-05-22 - Colloquium Department of Physics, Columbia University\n"
        "---------------------------------------\n"
        "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We made the case for local structure\n",
    ),
    (
        ["helper", "l_abstract", "--title", "graphitic"],
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--title", "graphitic", "--loc-inst", "upton"],
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--loc-inst", "upton"],
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--loc-inst", "upton", "--year", "2018"],
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--year", "2018"],
        "\n---------------------------------------\n"
        "2018-05-22 - Colloquium Department of Physics, Columbia University\n"
        "---------------------------------------\n"
        "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We made the case for local structure\n"
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--author", "scopatz"],
        "\n---------------------------------------\n"
        "2018-05-22 - Colloquium Department of Physics, Columbia University\n"
        "---------------------------------------\n"
        "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We made the case for local structure\n"
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--loc-inst", "upton", "--year", "2018"],
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--author", "scopatz", "--loc-inst", "upton"],
        "\n---------------------------------------\n"
        "2018-05-22 - 2018 NSLS-II and CFN Users Meeting, Upton NY\n"
        "---------------------------------------\n"
        "Title: ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function\n"
        "\nAnthony Scopatz\n"
        "\nAbstract: We pulled apart graphite with tape\n"
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        [
            "helper",
            "l_abstract",
            "--author",
            "scopatz",
            "--year",
            "2018",
            "--loc-inst",
            "upton",
            "--title",
            "graphitic",
        ],
        "\n---------------------------------------\n"
        "2018-05-22 - Meeting to check flexibility on dates, Upton NY\n"
        "---------------------------------------\n"
        "Title: Graphitic Dephenestration\n\n"
        "Anthony Scopatz, Anthony B Friend\n\n"
        "Abstract: We pulled apart graphite with tape\n",
    ),
    (
        ["helper", "l_abstract", "--loc-inst", "columbiau"],
        "\n---------------------------------------\n"
        "2018-05-22 - Colloquium Department of Physics, Columbia University\n"
        "---------------------------------------\n"
        "Title: Nanostructure challenges and successes from 16th Century warships to 21st Century energy\n\n"
        "Anthony Scopatz\n\n"
        "Abstract: We made the case for local structure\n",
    ),
    (
        ["helper", "l_todo", "--assigned-to", "sbillinge", "--date", "2020-05-01"],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(0)(89 days): (2) prepare the presentation (89|0|30.0|downtime|sbillinge|2saefa)\n"
        "     - about 10 minutes\n"
        "     - don't forget to upload to the website\n"
        "(2)(79 days): (1) read paper (79|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "2020-07-19(79 days): (1) read paper (79|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n",
    ),
    (
        [
            "helper",
            "l_todo",
            "--short",
            "65",
            "--date",
            "2020-07-13",
            "--assigned-by",
            "scopatz",
            "--assigned-to",
            "sbillinge",
        ],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(2)(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "2020-07-19(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n",
    ),
    (
        [
            "helper",
            "l_todo",
            "--tags",
            "downtime",
            "--date",
            "2020-07-13",
            "--assigned-by",
            "sbillinge",
            "--assigned-to",
            "sbillinge",
        ],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(0)(16 days): (2) prepare the presentation (16|0|30.0|downtime|sbillinge|2saefa)\n"
        "     - about 10 minutes\n"
        "     - don't forget to upload to the website\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n",
    ),
    (["helper", "l_todo", "--assigned-to", "wrong_id"], "The id you entered can't be found in todos.yml.\n"),
    (
        ["helper", "l_todo", "-o", "--date", "2021-4-10", "--assigned-to", "sbillinge", "--short"],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(0)(-255 days): (2) prepare the presentation (-255|0|30.0|downtime|sbillinge|2saefa)\n"
        "     - about 10 minutes\n"
        "     - don't forget to upload to the website\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n"
        "------------------------------\n"
        "Outstanding Reviews:\n"
        "------------------------------\n"
        "accepted:\n"
        "Manuscript by Wingit in Nature is due on 2021-04-11\n",
    ),
    (
        ["helper", "l_currentappointments", "-d", "2021-08-10"],
        "scopatz future_grant n/a 1.0 2020-09-01 2021-08-31\n",
    ),
    (["helper", "l_currentappointments", "-d", "2020-06-01"], "scopatz abc42 abc42 0.8 2020-06-01 2020-08-31\n"),
    (["helper", "l_currentappointments", "-d", "2020-01-01", "-s"], "scopatz sym sym 1.0 2020-01-01 2020-05-15\n"),
    (["helper", "v_meetings", "--test"], "Meeting validator helper\n"),
    (
        ["helper", "l_reimbstatus", "scopatz"],
        "Reimbursed expenses:\n"
        "\n"
        "Submitted expenses:\n"
        " - 180110 - testing the databallectionsse 2018-01-01 to 2018-01-10,\n"
        "   Expenses: unseg=550.00, Seg=0.00, Total=550.00, Where: Columbia, When: tbd\n"
        " - 180110 - testing the databallectionsse 2018-01-01 to 2018-01-10,\n"
        "   Expenses: unseg=550.00, Seg=0.00, Total=550.00, Where: Columbia, When: 2019-09-05\n"
        "   Grants: dmref15, SymPy-1.1\n"
        "this expense was used to get the work done\n"
        "\nUnsubmitted expenses:\n"
        "\nFuture expenses:\n",
    ),
    (
        ["helper", "l_reimbstatus", "sbillinge"],
        "Reimbursed expenses:\n"
        " - 190110 - testing 2019-01-01 to 2019-01-10,\n"
        "   Requested: 10.00, Reimbursed: 100.00, Date: 2019-09-15, Grants: SymPy-1.1\n"
        "\nSubmitted expenses:\n"
        "\nUnsubmitted expenses:\n"
        "\nFuture expenses:\n"
        "\nThese expenses have invalid statuses:\n"
        "test3\n",
    ),
    # these updaters are really listers because they list the current state
    (
        [
            "helper",
            "a_projectum",
            "New projectum",
            "lyang",
            "--date",
            "2020-04-29",
            "--collaborators",
            "afriend",
            "--description",
            "more work",
            "--group-members",
            "ascopatz",
            "--grants",
            "SymPy-1.1",
            "--due-date",
            "2021-01-01",
            "--notes",
            "new note",
        ],
        "ly_newprojectum has been added in projecta\n",
    ),
    (
        [
            "helper",
            "u_milestone",
            "--milestone_uuid",
            "kosb_fir",
            "--name",
            "Kick off meeting",
            "--date",
            "2020-05-07",
            "--objective",
            "introduce project to the lead",
            "--audience",
            "lead",
            "pi",
            "group_members",
            "--status",
            "converged",
            "--due-date",
            "2020-06-01",
            "--notes",
            "do this",
            "do that",
            "--type",
            "meeting",
            "--finish",
        ],
        "The milestone 'Kick off meeting' has been marked as finished in prum sb_firstprojectum.\n",
    ),
    (
        ["helper", "u_milestone", "--milestone_uuid", "bad_id"],
        "Failed to update projecta.\n"
        "No ids were found that match your milestone_uuid entry (bad_id).\n"
        "Make sure you have entered the correct uuid or uuid fragment and rerun the helper.\n\n",
    ),
    (
        [
            "helper",
            "u_milestone",
            "--milestone_uuid",
            "pl",
            "--status",
            "finished",
            "--due-date",
            "2023-01-01",
            "--notes",
            "do this",
            "do that",
            "--type",
            "mergedpr",
        ],
        "Failed to update projecta.\n"
        "Multiple ids match your milestone_uuid entry (pl).\n"
        "Try entering more characters of the uuid and rerun the helper.\n\n",
    ),
    (
        [
            "helper",
            "u_milestone",
            "--projectum_id",
            "pl",
            "--name",
            "new milestone",
            "--due_date",
            "2023-01-01",
            "--objective",
            "do all the things to complete this milestone",
            "--notes",
            "do this",
            "do that",
            "--type",
            "mergedpr",
        ],
        "Projectum not found. Projecta with similar names: \n"
        "pl_firstprojectum\n"
        "pl_secondprojectum\n"
        "pl_thirdprojectum\n"
        "Please rerun the helper specifying the complete ID.\n"
        "If your prum id looks correct, check that this id is in the collection "
        "in the database test.\n"
        "If this is not the case, rerun with --database set to the database where the item is located.\n",
    ),
    (
        ["helper", "u_logurl", "sb", "--index", "1", "https://docs.google.com/document/d/1pQMFpuI"],
        "sb_firstprojectum has been updated with a log_url of https://docs.google.com/document/d/1pQMFpuI\n",
    ),
    (
        ["helper", "u_logurl", "ly", "https://docs.google.com/document/d/1pQMFpuI"],
        "There does not seem to be a projectum with this exact name in this database.\n"
        "However, there are projecta with similar names: \n"
        "1. ly_newprojectum     current url: \n"
        "Please rerun the u_logurl helper with the same name as previously inputted, "
        "but with the addition of -i followed by a number corresponding to one of the "
        "above listed projectum ids that you would like to update.\n",
    ),
    (
        [
            "helper",
            "u_contact",
            "afriend",
            "--index",
            "2",
            "--notes",
            "Test note",
            "--aliases",
            "Friend",
            "--date",
            "2020-01-02",
        ],
        "afriend has been added/updated in contacts\n",
    ),
    (
        ["helper", "u_contact", "Anthony", "--date", "2020-01-02"],
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
        "   aliases: ['A. B. Friend', 'AB Friend', 'Tony Friend', 'Friend']\n",
    ),
    (
        ["helper", "u_contact", "Maria", "--date", "2020-01-02"],
        "Please rerun the helper by hitting up arrow and adding '-i list-index' to "
        "update the list item 'list-index', e.g., 'regolith helper eins -i 2'. For "
        "new contacts --name (-n) and --institution (-o) are required:\n"
        "1. Maria as a new contact\n",
    ),
    (
        [
            "helper",
            "a_todo",
            "test a_todo",
            "6",
            "50",
            "--assigned-to",
            "sbillinge",
            "--assigned-by",
            "sbillinge",
            "--begin-date",
            "2020-07-06",
            "--importance",
            "2",
            "--deadline",
            "--notes",
            "test notes 1",
            "test notes 2",
            "--tags",
            "tag1",
            "tag2",
            "--date",
            "2020-07-10",
            "--milestone_uuid",
            "milestone_uuid_sb1_2",
        ],
        "The milestone uuid milestone_uuid_sb1_2 in projectum sb_firstprojectum has been updated in projecta.\n"
        'The task "test a_todo" for sbillinge has been added in todos collection.\n',
    ),
    (
        [
            "helper",
            "f_todo",
            "--index",
            "3",
            "--assigned-to",
            "sbillinge",
            "--end-date",
            "2020-07-20",
            "--date",
            "2020-07-13",
        ],
        'The task "(3) test a_todo" in test for sbillinge has been marked as finished.\n',
    ),
    (
        ["helper", "f_todo", "--assigned-to", "sbillinge", "--date", "2020-07-13"],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "Please choose from one of the following to update:\n"
        "(index) action (days to due date|importance|expected duration (mins)|tags|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(0)(16 days): (2) prepare the presentation (16|0|30.0|downtime|sbillinge|2saefa)\n"
        "     - about 10 minutes\n"
        "     - don't forget to upload to the website\n"
        "(2)(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "2020-07-19(6 days): (1) read paper (6|2|60.0|reading,downtime|scopatz|1saefa)\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n",
    ),
    (
        ["helper", "f_todo", "--index", "99100"],
        "WARNING: indices >= 9900 are used for milestones which should be finished using u_milestone and not f_todo\n",
    ),
    (
        [
            "helper",
            "u_todo",
            "--index",
            "3",
            "--assigned-to",
            "sbillinge",
            "--description",
            "update the description",
            "--due-date",
            "2020-07-06",
            "--estimated-duration",
            "35",
            "--importance",
            "2",
            "--status",
            "finished",
            "--notes",
            "some new notes",
            "notes2",
            "--tags",
            "newtag1",
            "newtag2",
            "--begin-date",
            "2020-06-06",
            "--deadline",
            "t",
            "--end-date",
            "2020-07-07",
            "--date",
            "2020-07-13",
        ],
        'The task "(3) test a_todo" in test for sbillinge has been updated.\n',
    ),
    (
        [
            "helper",
            "u_todo",
            "--assigned-to",
            "sbillinge",
            "--stati",
            "started",
            "finished",
            "--filter",
            "description",
            "the",
            "--date",
            "2020-07-13",
        ],
        "If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r\n"
        "Please choose from one of the following to update:\n"
        "(index) action (days to due date|importance|expected duration (mins)|assigned by)\n"
        "--------------------------------------------------------------------------------\n"
        "started:\n"
        "(0)(16 days): (2) prepare the presentation (16|0|30.0|downtime|sbillinge|2saefa)\n"
        "     - about 10 minutes\n"
        "     - don't forget to upload to the website\n"
        "finished:\n"
        "(2020-07-07): (3) update the description (-7|2|35.0|tag1,tag2,newtag1,newtag2|sbillinge|test-u)\n"
        "     - test notes 1\n"
        "     - test notes 2\n"
        "     - some new notes\n"
        "     - notes2\n"
        "----------------------------------------------------------------------------\n"
        "(importance)(days to due): (Task number) Task (decreasing priority going up)\n"
        "----------------------------------------------------------------------------\n"
        "2020-07-06(-7 days): (3) update the description (-7|2|35.0|tag1,tag2,newtag1,newtag2|sbillinge|test-u)\n"
        "     - test notes 1\n"
        "     - test notes 2\n"
        "     - some new notes\n"
        "     - notes2\n"
        "------------------------------\n"
        "Deadlines:\n"
        "------------------------------\n",
    ),
    (
        ["helper", "u_todo", "--index", "99100"],
        "WARNING: indices >= 9900 are used for milestones which should be updated using u_milestone and not u_todo\n",
    ),
    (
        ["helper", "f_prum", "sb_firstprojectum", "--end-date", "2020-07-01"],
        "sb_firstprojectum status has been updated to finished\n",
    ),
    (
        ["helper", "f_prum", "sb_"],
        "Projectum not found. Projecta with similar names: \n"
        "sb_firstprojectum     status:finished\n"
        "Please rerun the helper specifying the complete ID.\n",
    ),
    (["helper", "lister", "people"], "Results of your search:\nabeing    \nsbillinge    \nscopatz\n"),
    (["helper", "lister", "people", "--kv-filter", "name", "simon"], "Results of your search:\n" "sbillinge\n"),
    (
        ["helper", "lister", "people", "--kv-filter", "name", "simon", "--return-fields", "name", "position"],
        "Results of your search:\nsbillinge    name: Simon J. L. Billinge    position: professor\n",
    ),
    (
        ["helper", "lister", "people", "--keys"],
        "Available keys:\n"
        "['_id', 'active', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
        "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
        "'github_id', 'google_scholar_url', 'grp_mtg_active', 'hindex', "
        "'home_address', 'initials', 'linkedin_url', "
        "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
        "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
        "'title']\n",
    ),
    (
        ["helper", "lister", "people", "--kv-filter", "name", "simon", "--keys"],
        "Results of your search:\nsbillinge\n"
        "Available keys:\n"
        "['_id', 'active', 'activities', 'aka', 'appointments', 'avatar', 'bio', 'bios', "
        "'committees', 'education', 'email', 'employment', 'facilities', 'funding', "
        "'github_id', 'google_scholar_url', 'grp_mtg_active', 'hindex', "
        "'home_address', 'initials', 'linkedin_url', "
        "'membership', 'miscellaneous', 'name', 'office', 'orcid_id', 'position', "
        "'publicity', 'research_focus_areas', 'service', 'skills', 'teaching', "
        "'title']\n",
    ),
    (
        ["helper", "lister", "people", "--kv-filter", "name", "simon", "position", "singer"],
        "There are no results that match your search.\n",
    ),
    (
        [
            "helper",
            "u_institution",
            "columbiau",
            "--aka",
            "ucolumbia",
            "Columbia University in the City of New York",
            "--dept-id",
            "mathematics",
            "--dept-name",
            "Department of Mathematics",
            "--dept-aka",
            "dept. of mathematics",
            "math department",
            "--school-id",
            "cc",
            "--school-name",
            "Columbia College",
            "--school-aka",
            "CC",
            "--date",
            "2020-01-01",
        ],
        "columbiau has been updated/added in institutions\n",
    ),
    (
        ["helper", "u_institution", "col"],
        "Please rerun the helper specifying '-n list-index' to update item number 'list-index':\n"
        "1. col as a new institution.\n"
        "2. columbiau      Columbia University.\n",
    ),
    (
        ["helper", "makeappointments", "run", "--no-gui", "--projection-from-date", "2020-08-31"],
        "WARNING: appointment gap for scopatz from 2019-02-01 to 2019-12-31\n"
        "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
        "appointments on outdated grants:\n"
        "    person: scopatz, appointment: s20, grant: sym,\n"
        "            from 2020-01-01 until 2020-05-15\n"
        "appointments on depleted grants:\n"
        "    person: scopatz, appointment: f19, grant: dmref15,\n"
        "            from 2019-02-07 until 2019-03-31\n"
        "    person: scopatz, appointment: ss20, grant: abc42,\n"
        "            from 2020-07-15 until 2020-08-31\n"
        "    person: scopatz, appointment: ss21, grant: future_grant,\n"
        "            from 2020-09-06 until 2021-08-31\n"
        "underspent grants:\n"
        "    dmref15: end: 2019-05-01\n"
        "      projected underspend: 54.55 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: -3.41\n"
        "    sym: end: 2030-12-31\n"
        "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: 0.06\n"
        "cumulative underspend = 62.55 months, cumulative months to support = 0\n"
        "overspent grants:\n"
        "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
        "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n"
        "plotting mode is on\n",
    ),
    (
        ["helper", "makeappointments", "run", "--no-gui", "--projection-from-date", "2020-08-31", "-v"],
        "WARNING: appointment gap for scopatz from 2019-02-01 to 2019-12-31\n"
        "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
        "appointments on outdated grants:\n"
        "    person: scopatz, appointment: s20, grant: sym,\n"
        "            from 2020-01-01 until 2020-05-15\n"
        "appointments on depleted grants:\n"
        "    person: scopatz, appointment: f19, grant: dmref15,\n"
        "            from 2019-02-07 until 2019-03-31\n"
        "    person: scopatz, appointment: ss20, grant: abc42,\n"
        "            from 2020-07-15 until 2020-08-31\n"
        "    person: scopatz, appointment: ss21, grant: future_grant,\n"
        "            from 2020-09-06 until 2021-08-31\n"
        "underspent grants:\n"
        "    dmref15: end: 2019-05-01\n"
        "      projected underspend: 54.55 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: -3.41\n"
        "    sym: end: 2030-12-31\n"
        "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: 0.06\n"
        "cumulative underspend = 62.55 months, cumulative months to support = 0\n"
        "overspent grants:\n"
        "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
        "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n"
        "plotting mode is on\n",
    ),
    (
        ["helper", "makeappointments", "run", "--no-plot", "--projection-from-date", "2020-08-31"],
        "WARNING: appointment gap for scopatz from 2019-02-01 to 2019-12-31\n"
        "WARNING: appointment gap for scopatz from 2020-05-16 to 2020-08-31\n"
        "appointments on outdated grants:\n"
        "    person: scopatz, appointment: s20, grant: sym,\n"
        "            from 2020-01-01 until 2020-05-15\n"
        "appointments on depleted grants:\n"
        "    person: scopatz, appointment: f19, grant: dmref15,\n"
        "            from 2019-02-07 until 2019-03-31\n"
        "    person: scopatz, appointment: ss20, grant: abc42,\n"
        "            from 2020-07-15 until 2020-08-31\n"
        "    person: scopatz, appointment: ss21, grant: future_grant,\n"
        "            from 2020-09-06 until 2021-08-31\n"
        "underspent grants:\n"
        "    dmref15: end: 2019-05-01\n"
        "      projected underspend: 54.55 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: -3.41\n"
        "    sym: end: 2030-12-31\n"
        "      projected underspend: 8.0 months, balance as of 2020-08-31: 0\n"
        "      required ss+gra burn: 0.06\n"
        "cumulative underspend = 62.55 months, cumulative months to support = 0\n"
        "overspent grants:\n"
        "    end: 2020-12-31, grant: abc42, overspend amount: -1.41 months\n"
        "    end: 2026-08-30, grant: future_grant, overspend amount: -11.97 months\n",
    ),
    (
        [
            "helper",
            "a_proprev",
            "A. Einstein",
            "nsf",
            "2020-04-08",
            "-q",
            "Tess Guebre",
            "--status",
            "downloaded",
            "--title",
            "A flat world theory",
        ],
        "A. Einstein proposal has been added/updated in proposal reviews\n",
    ),
    (
        [
            "helper",
            "a_manurev",
            "Einstein",
            "2020-09-15",
            "Nature",
            "On the Quantum Theory of Radiation",
            "--requester",
            "Niels Bohr",
            "--reviewer",
            "zcliu",
            "--status",
            "submitted",
            "--submitted-date",
            "2019-01-01",
        ],
        "Einstein manuscript has been added/updated in manuscript reviews\n",
    ),
    (
        [
            "helper",
            "a_grppub_readlist",
            "pdf",
            "--title",
            "A list to test the lister",
            "--purpose",
            "Test the lister",
            "--date",
            "2021-04-01",
        ],
        "Making lists for tags:\n['pdf']\npdf has been added/updated in reading_lists\n",
    ),
    (
        [
            "helper",
            "a_proposal",
            "a new proposal",
            "100.0",
            "To destroy numbers",
            "--begin-date",
            "2020-09-15",
            "--end-date",
            "2022-02-14",
            "--duration",
            "16.89",
            "--authors",
            "Kurt Godel",
            "MC Escher",
            "Johann Sebastian Bach",
            "--currency",
            "Bitcoin",
            "--other-agencies",
            "Flatland",
            "--notes",
            "this is a sample added proposal",
            "--date",
            "2020-08-01",
        ],
        "20_anewproposal has been added in proposals\n",
    ),
    # This now tested in the test_helper_python_mock function, below
    # (["helper", "a_expense", "timbuktoo", "travel to timbuktoo", "--amount", "159.18",
    #   "--grants", "mrsec14", "dmref15", "--payee", "ashaaban",
    #   "--where", "bank", "--begin-date", "2020-06-20", "--end-date", "2020-06-25"],
    #  "2006as_timbuktoo has been added in expenses\n"),
    # The following Test Cases A-D test adding presentation-related expenses and map to user stories for Issue #910. All except one are commented out
    # because the current testing architecture (1) limits our ability to validate the addition of more than one entry to a collection, and
    # (2) only spins up one test database, but two would be needed to test a different destination database for expense data. The hope is
    # that, in the future when the test architecture is improved or changed, these commented-out tests can be useful and enable fully testing the added functionality.
    # Test Case A: Expect a new entry in outputs/presentations/presentations.yaml
    # (["helper", "a_presentation", "flat earth", "Mars", "2020-06-26", "2020-06-26",
    #   "--type", "contributed_oral", "--person", "ashaaban", "--grants", "mrsec14",
    #   "--authors", "sbillinge", "ashaaban", "--abstract", "the earth is round as seen from mars",
    #   "--title", "On the roundness of the Earth", "--status", "in-prep",
    #   "--notes", "this is a sample added presentation",
    #   "--presentation-url", "http://drive.google.com/SEV356DV",
    #   "--no-cal", "--no-expense"],
    #  "2006as_mars has been added in presentations\n"),
    # Test Case B: user arguments contradict, raises error
    # (["helper", "a_presentation", "Test Case B", "Test B", "2020-06-26", "2020-06-26",
    #   "--type", "contributed_oral", "--person", "nasker", "--grants", "testing",
    #   "--authors", "sbillinge", "nasker", "--abstract", "testing",
    #   "--title", "Testing Case B", "--status", "in-prep",
    #   "--notes", "This is to test Case B, where user contradicts themselves by passing both --no-expense and --expense_db",
    #   "--presentation-url", "http://drive.google.com/SEV356DV",
    #   "--no-cal", "--no-expense", "--expense-db testB"],
    #  pytest.raises(RuntimeError)),
    # Test Case C.1: user wants an expense added, but did not specify an expense db, and default is public
    # (["helper", "a_presentation", "Test Case C.1", "Test C.1", "2020-06-26", "2020-06-26",
    #   "--type", "contributed_oral", "--person", "nasker", "--grants", "testing",
    #   "--authors", "sbillinge", "nasker", "--abstract", "testing",
    #   "--title", "Testing Case C.1", "--status", "in-prep",
    #   "--notes", "This is to test Case C.1, where user wants an expense added, but did not specify an expense db, and the first db in the regolithrc.json file is public, so the program errors.",
    #   "--presentation-url", "http://drive.google.com/SEV356DV",
    #   "--no-cal"],
    #  pytest.raises(RuntimeError)),
    # Test Case C.2: user wants an expense added, and passed the force option without specifying an expense db, and default is public
    # This is tested in the test_helper_python_mock function, below
    # (["helper", "a_presentation", "Test Case C.2", "Test C.2", "2020-06-26", "2020-06-26",
    #   "--type", "contributed_oral", "--person", "nasker", "--grants", "testing",
    #   "--authors", "sbillinge", "nasker", "--abstract", "testing",
    #   "--title", "Testing Case C.2", "--status", "in-prep",
    #   "--notes", "This is to test Case C.2 where user wants an expense added and passed the force option without specifying an expense db when default is public",
    #   "--presentation-url", "http://drive.google.com/SEV356DV",
    #   "--no-cal", "--force", "--no-repo"], # Expect a new presentation and new expense in db 'test'.
    #    "2006na_testc.2 has been added in presentations\n2006na_testc.2 has been added in expenses in database test\n"),
    # Test Case D: user wants an expense added, and specified an expense db
    # (["helper", "a_presentation", "Test Case D", "Test D", "2020-06-26", "2020-06-26",
    #   "--type", "contributed_oral", "--person", "nasker", "--grants", "testing",
    #   "--authors", "sbillinge", "nasker", "--abstract", "testing",
    #   "--title", "Testing Case D", "--status", "in-prep",
    #   "--notes", "This is to test Case D, where user wants an expense added, and specified an expense-db",
    #   "--presentation-url", "http://drive.google.com/SEV356DV",
    #   "--no-cal", "--expense-db private-test"], # Expect a new presentation and new expense in db 'private-test'
    #    "2006na_testd has been added in presentations\n2006na_testd has been added in expenses in database private-test\n"),
]

db_srcs = [
    # "mongo",
    "fs"
]

# helper_map = [
#     (["helper", "a_grppub_readlist", "all", "all"
#      ],
#      "List of all tags in citations collection:\n['nomonth', 'pdf']\nbuilding lists for all tags in the citation collection\nnomonth has been added/updated in reading_lists\npdf has been added/updated in reading_lists\n"),
#     ]

helper_map_bad = [
    (
        ["helper", "u_milestone", "--milestone_uuid", "sb_fir", "--projectum_id", "sb_firstprojectum"],
        "Detected both a uuid fragment and projectum id.\n"
        "You may enter either a milestone uuid or a projectum id but not both.\n"
        "Enter a milestone uuid to update an existing milestone, or a projectum id to add a new milestone to that projectum.\n",
        RuntimeError,
    ),
    (
        [
            "helper",
            "u_milestone",
            "--due-date",
            "2020-06-01",
            "--notes",
            "do this",
            "do that",
            "--type",
            "mergedpr",
        ],
        "No milestone uuid or projectum id was entered.\n"
        "Enter a milestone uuid to update an existing milestone, or a projectum id to add a new milestone to that projectum.\n",
        RuntimeError,
    ),
    (
        ["helper", "u_milestone", "--projectum_id", "sb_firstprojectum", "--due_date", "2020-06-01"],
        "name, objective, and due date are required for a new milestone",
        RuntimeError,
    ),
    (
        ["helper", "u_milestone", "--milestone_uuid", "milestone_uuid_pl1", "--due_date", "2020-06-01"],
        "Milestone (milestone_uuid_pl1) does not have a type set and this is required.\n"
        "Specify '--type' and rerun the helper to update this milestone.\n",
        ValueError,
    ),
    (
        ["helper", "u_milestone", "--milestone_uuid", "kopl_first", "--type", "bad_type"],
        "The type you have specified is not recognized. \n"
        "Please rerun your command adding '--type' \n"
        "and giving a type from this list:\n"
        f"{MILESTONE_TYPES}\n",
        ValueError,
    ),
    (
        [
            "helper",
            "u_milestone",
            "--projectum_id",
            "sb_firstprojectum",
            "-u",
            "2020-06-01",
            "-n",
            "new milestone",
            "-o",
            "complete ms",
            "--type",
            "bad_type",
        ],
        "The type you have specified is not recognized. \n"
        "Please rerun your command adding '--type' \n"
        "and giving a type from this list:\n"
        f"{MILESTONE_TYPES}\n",
        ValueError,
    ),
    (
        ["helper", "u_milestone", "--milestone_uuid", "milestone_uuid_sb1_", "--type", "bad_type"],
        "The type you have specified is not recognized. \n"
        "Please rerun your command adding '--type' \n"
        "and giving a type from this list:\n"
        f"{MILESTONE_TYPES}\n",
        ValueError,
    ),
    (
        ["helper", "a_todo", "test a_todo", "6", "50", "--assigned-to", "sbillinge", "--milestone_uuid", "bad_id"],
        "No milestone ids were found that match your entry (bad_id).\n"
        "Make sure you have entered the correct milestone uuid or uuid fragment and rerun the helper.",
        RuntimeError,
    ),
    (
        [
            "helper",
            "a_todo",
            "test a_todo",
            "6",
            "50",
            "--assigned-to",
            "sbillinge",
            "--milestone_uuid",
            "one_uuid",
        ],
        "Multiple milestone ids match your entry (one_uuid).\n"
        "Try entering more characters of the uuid and rerunning the helper.",
        RuntimeError,
    ),
    (
        ["helper", "a_todo", "test a_todo", "6", "50", "--assigned-to", "sbillinge", "--milestone_uuid", "_sb1"],
        "Multiple milestone ids match your entry (_sb1).\n"
        "Try entering more characters of the uuid and rerunning the helper.",
        RuntimeError,
    ),
]


@pytest.mark.parametrize("hmb", helper_map_bad)
def test_helpers_bad(hmb, make_db):
    repo = Path(make_db)
    os.chdir(repo)
    with pytest.raises(hmb[2]) as excinfo:
        main(args=hmb[0])
    assert str(excinfo.value) == hmb[1]


@pytest.mark.parametrize("db_src", db_srcs)
@pytest.mark.parametrize("hm", helper_map)
def test_helper_python(hm, make_db, db_src, make_mongodb, capsys, mocker):
    mocker.patch("uuid.uuid4", return_value="test-uuid")
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
    assert hm[1] == out

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
                mongo_database = client[rc.databases[0]["name"]]
                assert_mongo_vs_yaml_outputs(expecteddir, mongo_database)


helper_map_loose = [
    (
        ["helper", "l_abstract"],
        "-------------------------------------------\n"
        "please rerun specifying at least one filter\n"
        "-------------------------------------------\n",
    ),
]


@pytest.mark.parametrize("hm", helper_map_loose)
def test_helper_python_loose(hm, make_db, capsys):
    repo = Path(make_db)
    os.chdir(repo)

    main(args=hm[0])
    out, err = capsys.readouterr()
    assert hm[1] in out


helper_map_requests = [
    (
        [
            "helper",
            "a_expense",
            "timbuktoo",
            "travel to timbuktoo",
            "--amount",
            "159.18",
            "--grants",
            "mrsec14",
            "dmref15",
            "--payee",
            "ashaaban",
            "--where",
            "bank",
            "--begin-date",
            "2020-06-20",
            "--end-date",
            "2020-06-25",
        ],
        "2006as_timbuktoo has been added in expenses\n",
    ),
    (
        [
            "helper",
            "a_presentation",
            "Test Case C.2",
            "Test C.2",
            "2020-06-26",
            "2020-06-26",
            "--type",
            "contributed_oral",
            "--person",
            "nasker",
            "--grants",
            "testing",
            "--authors",
            "sbillinge",
            "nasker",
            "--abstract",
            "testing",
            "--title",
            "Testing Case C.2",
            "--status",
            "in-prep",
            "--notes",
            "This is to test Case C.2 where user wants an expense added and passed the force option without specifying an expense db when default is public",
            "--presentation-url",
            "http://drive.google.com/SEV356DV",
            "--no-cal",
            "--force",
            "--repo",
        ],  # Expect a new presentation and new expense in db 'test'
        "2006na_testc.2 has been added in presentations\n2006na_testc.2 has been added in expenses in database test\nrepo 2006na_testc.2 has been created at https://example.com.\nClone this to your local using (HTTPS):\ngit clone https://example.com:talks/2006na_testc.2.git\nor (SSH):\ngit clone git@example.com:talks/2006na_testc.2.git\n",
    ),
]


@pytest.mark.parametrize("db_src", db_srcs)
@pytest.mark.parametrize("hmr", helper_map_requests)
@requests_mock.Mocker(kw="mock")
def test_helper_python_mock(hmr, make_db, db_src, make_mongodb, capsys, **kwargs):
    testfile = Path(__file__)

    kwargs["mock"].post(
        "https://example.com/url/example?namespace_id=35&initialize_with_readme=true&name=2006na_testc.2"
    )

    if db_src == "fs":
        repo = Path(make_db)
    elif db_src == "mongo":
        if make_mongodb is False:
            pytest.skip("Mongoclient failed to start")
        else:
            repo = Path(make_mongodb)
    os.chdir(repo)

    main(args=hmr[0])
    out, err = capsys.readouterr()
    assert hmr[1] == out

    expecteddir = testfile.parent / "outputs" / hmr[0][1]

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
                mongo_database = client[rc.databases[0]["name"]]
                assert_mongo_vs_yaml_outputs(expecteddir, mongo_database)


def assert_mongo_vs_yaml_outputs(expecteddir, mongo_database):
    from regolith.dates import convert_doc_iso_to_date
    from regolith.fsclient import load_yaml
    from regolith.mongoclient import load_mongo_col

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

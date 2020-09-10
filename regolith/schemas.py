"""Database schemas, examples, and tools"""
import copy
from warnings import warn

from cerberus import Validator

from .sorters import POSITION_LEVELS

SORTED_POSITION = sorted(POSITION_LEVELS.keys(), key=POSITION_LEVELS.get)
PRESENTATIONS_TYPE = ["award", "colloquium", "contributed_oral", "invited", "keynote",
                      "plenary", "poster", "seminar", "tutorial"]
APPOINTMENTS_TYPE = ["gra", "ss", "pd", "ug"]

EXEMPLARS = {
    "abstracts": {
        "_id": "Mouginot.Model",
        "coauthors": "P.P.H. Wilson",
        "email": "mouginot@wisc.edu",
        "firstname": "Baptiste",
        "institution": "University of Wisconsin-Madison",
        "lastname": "Mouginot",
        "references": "[1] B. MOUGINOT, “cyCLASS: CLASS "
                      "models for Cyclus,”, Figshare, "
                      "https://dx.doi.org/10.6084/"
                      "m9.figshare.3468671.v2 (2016).",
        "text": "The CLASS team has developed high "
                "quality predictors based on pre-trained "
                "neural network...",
        "timestamp": "5/5/2017 13:15:59",
        "title": "Model Performance Analysis",
    },
    "assignments": {
        "_id": "hw01-rx-power",
        "category": "homework",
        "courses": ["EMCH-558-2016-S", "EMCH-758-2016-S"],
        "points": [1, 2, 3],
        "questions": ["1-9", "1-10", "1-12"],
    },
    "beamplan": {
        '_id': "test",
        'beamtime': '2020-1-XPD',
        'begin_date': '2020-01-01',
        'end_date': '2020-01-02',
        'devices': ['cryostream'],
        'exp_plan': ['load samples on the holder',
                     'scan the holder to locate the samples',
                     'take room temperature measurement of sample and the subtrate',
                     'ramp down temperature to 100K',
                     'ramp up, measure PDF at temperature 100K ~ 300K, 10K stepsize, 1 min exposure'],
        'holder': 'film holder (1 cm * 1 cm * 1 mm)',
        'measurement': 'Tramp',
        'objective': 'temperature ramping PDF of one WO3 film (100, 300K, 10K)',
        'pipeline': 'usual',
        'prep_plan': ['films will be made by kriti'],
        'project': '20ks_wo3',
        'project_lead': 'kseth',
        'samples': ['WO3 film', 'glass subtrate'],
        'scanplan': ['Scanplan(bt, Tramp, 30, 80, 500, 10)'],
        'ship_plan': ['seal and ship to CU', 'carry to the beamline'],
        'time': 190,
        'todo': ["todo something"]},
    "beamtime": {
        "_id": "2020-1-XPD",
        "begin_date": "2020-02-14",
        "begin_time": "8:00 am",
        "end_date": "2020-02-17",
        "end_time": "8:00 am"
    },
    "blog": {
        "_id": "my-vision",
        "author": "Anthony Scopatz",
        "day": 18,
        "month": "September",
        "original": "https://scopatz.com/my-vision/",
        "post": "I would like see things move forward. Deep, I know!",
        "title": "My Vision",
        "year": 2015,
    },
    "citations": {
        "_id": "meurer2016sympy",
        "author": [
            "Meurer, Aaron",
            "Smith, Christopher P",
            "Paprocki, Mateusz",
            "{\\v{C}}ert{\\'\\i}k, Ond{\\v{r}}ej",
            "Rocklin, Matthew",
            "Kumar, AMiT",
            "Ivanov, Sergiu",
            "Moore, Jason K",
            "Singh, Sartaj",
            "Rathnayake, Thilina",
            "Sean Vig",
            "Brian E Granger",
            "Richard P Muller",
            "Francesco Bonazzi",
            "Harsh Gupta",
            "Shivam Vats",
            "Fredrik Johansson",
            "Fabian Pedregosa",
            "Matthew J Curry",
            "Ashutosh Saboo",
            "Isuru Fernando",
            "Sumith Kulal",
            "Robert Cimrman",
            "Anthony Scopatz",
        ],
        "doi": "10.1021/nn501591g",
        "entrytype": "article",
        "journal": "PeerJ Computer Science",
        "month": "Jan",
        "pages": "e103",
        "publisher": "PeerJ Inc. San Francisco, USA",
        "synopsis": "The description of symbolic computing in Python",
        "tags": "pdf",
        "title": "SymPy: Symbolic computing in Python",
        "volume": "4",
        "year": "2017",
    },
    "contacts": {
        "_id": "afriend",
        "aka": [
            "A. B. Friend",
            "AB Friend",
            "Tony Friend"
        ],
        "department": "physics",
        "email": "friend@deed.com",
        "institution": "columbiau",
        "name": "Anthony B Friend",
        "notes": ["The guy I meet for coffee sometimes"],
        "title": "Mr.",
        "month": "January",
        "year": 2020,
        "day": 15,
        "uuid": "76f2a4c7-aa63-4fa3-88b5-396b0c15d368",
    },
    "courses": {
        "_id": "EMCH-552-2016-F",
        "active": False,
        "department": "EMCH",
        "number": 552,
        "scale": [
            [0.875, "A"],
            [0.8125, "B+"],
            [0.75, "B"],
            [0.6875, "C+"],
            [0.625, "C"],
            [0.5625, "D+"],
            [0.5, "D"],
            [-1.0, "F"],
        ],
        "season": "F",
        "students": ["Human A. Person", "Human B. Person"],
        "syllabus": "emch552-2016-f-syllabus.pdf",
        "weights": {
            "class-notes": 0.15,
            "final": 0.3,
            "homework": 0.35,
            "midterm": 0.2,
        },
        "year": 2016,
    },
    "expenses": {
        "_id": "test",
        "expense_type": "business",
        "grant_percentages": ["50", "50"],
        "grants": ["dmref15", "SymPy-1.1"],
        "itemized_expenses": [
            {
                "day": i,
                "month": "Jan",
                "year": 2018,
                "purpose": "test",
                "unsegregated_expense": 10 * i,
                "segregated_expense": 0,
            }
            for i in range(1, 11)
        ],
        "payee": "scopatz",
        "project": "Cyclus",
        "overall_purpose": "testing the databallectionsse",
    },
    "grades": {
        "_id": "Human A. Person-rx-power-hw02-EMCH-758-2017-S",
        "student": "hap",
        "assignment": "2017-rx-power-hw02",
        "course": "EMCH-758-2017-S",
        "scores": [1, 1.6, 3],
    },
    "grants": [
        {
            "_id": "SymPy-1.1",
            "amount": 3000.0,
            "alias": "sym",
            "begin_day": 1,
            "begin_month": "May",
            "begin_year": 2030,
            "call_for_proposals": "https://groups.google.com/d/msg"
                                  "/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
            "end_day": 31,
            "end_month": "December",
            "end_year": 2030,
            "funder": "NumFOCUS",
            "narrative": "https://docs.google.com/document/d/1nZxqoL"
                         "-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp"
                         "=sharing",
            "program": "Small Development Grants",
            "team": [
                {
                    "institution": "University of South Carolina",
                    "name": "Anthony Scopatz",
                    "position": "pi",
                },
                {
                    "institution": "University of South Carolina",
                    "name": "Aaron Meurer",
                    "position": "researcher",
                },
            ],
            "status": "pending",
            "title": "SymPy 1.1 Release Support",
            "budget": [
                {"begin_date": "2030-05-01",
                 "end_date": "2030-06-30",
                 "student_months": 0.5,
                 "postdoc_months": 0.0,
                 "ss_months": 1.0,
                 "amount": 1000.0,
                 },
                {"begin_date": "2030-07-01",
                 "end_date": "2030-09-30",
                 "student_months": 1.5,
                 "postdoc_months": 0.0,
                 "ss_months": 2.0,
                 "amount": 1000.0,
                 },
                {"begin_date": "2030-10-01",
                 "end_date": "2030-12-31",
                 "student_months": 3.0,
                 "postdoc_months": 0.0,
                 "ss_months": 0.0,
                 "amount": 1000.0,
                 },
            ],
            "proposal_id": "SymPy-1.1"
        },
        {
            "_id": "SymPy-2.0",
            "amount": 3000.0,
            "alias": "sym2.0",
            "begin_day": 1,
            "begin_month": 6,
            "begin_year": 2019,
            "call_for_proposals": "https://groups.google.com/d/msg"
                                  "/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
            "end_day": 31,
            "end_month": "December",
            "end_year": 2030,
            "funder": "NumFOCUS",
            "narrative": "https://docs.google.com/document/d/1nZxqoL"
                         "-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp"
                         "=sharing",
            "program": "Small Development Grants",
            "team": [
                {
                    "institution": "University of South Carolina",
                    "name": "Anthony Scopatz",
                    "position": "pi",
                },
                {
                    "institution": "University of South Carolina",
                    "name": "Aaron Meurer",
                    "position": "researcher",
                },
            ],
            "status": "pending",
            "title": "SymPy 1.1 Release Support",
            "budget": [
                {"begin_date": "2019-06-01",
                 "end_date": "2024-12-31",
                 "student_months": 12.0,
                 "postdoc_months": 24.0,
                 "ss_months": 14.0,
                 "amount": 1500.0,
                 },
                {"begin_date": "2025-01-01",
                 "end_date": "2030-12-31",
                 "student_months": 12.0,
                 "postdoc_months": 24.0,
                 "ss_months": 0.0,
                 "amount": 1500.0,
                 },
            ],
            "proposal_id": "SymPy-2.0",
        },
        {
            "_id": "dmref15",
            "alias": "dmref15",
            "account": "GG012345",
            "amount": 982785.0,
            "funder": "NSF",
            "grant_id": "DMREF-1534910",
            "institution": "Columbia University",
            "notes": "Designing Materials to Revolutionize and Engineer our "
                     "Future (DMREF)",
            "person_months_academic": 0.0,
            "person_months_summer": 0.25,
            "program": "DMREF",
            "scope": "This grant is to develop complex modeling methods for regularizing "
                     "ill-posed nanostructure inverse problems using data analytic and "
                     "machine learning based approaches. This does not overlap with any "
                     "other grant.",
            "team": [
                {
                    "institution": "Columbia University",
                    "name": "qdu",
                    "position": "co-pi",
                },
                {
                    "institution": "Columbia University",
                    "name": "dhsu",
                    "position": "co-pi",
                },
                {
                    "institution": "Columbia University",
                    "name": "Anthony Scopatz",
                    "position": "pi",
                    "subaward_amount": 330000.0,
                },
            ],
            "title": "DMREF: Novel, data validated, nanostructure determination "
                     "methods for accelerating materials discovery",
            "budget": [
                {"begin_date": "2018-05-01",
                 "end_date": "2018-09-30",
                 "student_months": 12.0,
                 "postdoc_months": 0.0,
                 "ss_months": 6.0,
                 "amount": 327595.0,
                 },
                {"begin_date": "2018-10-01",
                 "end_date": "2019-01-30",
                 "student_months": 8.0,
                 "postdoc_months": 0.0,
                 "ss_months": 12.0,
                 "amount": 327595.0,
                 },
                {"begin_date": "2019-02-01",
                 "end_date": "2019-05-01",
                 "student_months": 12.0,
                 "postdoc_months": 0.0,
                 "ss_months": 6.0,
                 "amount": 327595.0,
                 },
            ],
            "proposal_id": "dmref15"
        },
        {"_id": "abc42",
         "alias": "abc42",
         "amount": 42000.0,
         "begin_date": "2020-06-01",
         "end_date": "2020-12-31",
         "funder": "Life",
         "program": "Metaphysical Grants",
         "team": [
             {"institution": "University of Pedagogy",
              "name": "Chief Pedagogue",
              "position": "pi"
              },
             {"institution": "University of Pedagogy",
              "name": "Pedagogue Jr.",
              "position": "co-pi"
              },
         ],
         "title": "The answer to life, the universe, and everything",
         "budget": [
             {"begin_date": "2020-06-01",
              "end_date": "2020-12-31",
              "student_months": 0.0,
              "postdoc_months": 0.0,
              "ss_months": 1.0,
              "amount": 42000.0,
              }
         ],
         "proposal_id": "abc42",
         },
        {"_id": "ta",
         "amount": 0.0,
         "begin_date": "2020-06-01",
         "end_date": "2020-12-31",
         "funder": "Life",
         "program": "Underground Grants",
         "team": [
             {"institution": "Ministry of Magic",
              "name": "Chief Witch",
              "position": "pi"
              },
             {"institution": "Ministry of Magic",
              "name": "Chief Wizard",
              "position": "co-pi"
              },
         ],
         "title": "Support for teaching assistants",
         "budget": [
             {"begin_date": "2020-06-01",
              "end_date": "2020-08-30",
              "student_months": 0.0,
              "postdoc_months": 0.0,
              "ss_months": 0.0,
              "amount": 0.0,
              }
         ]
         },
    ],
    "groups": {
        "_id": "ergs",
        "pi_name": "Anthony Scopatz",
        "department": "Mechanical Engineering",
        "institution": "University of South Carolina",
        "name": "ERGS",
        "aka": ["Energy Research Group Something", "Scopatz Group"],
        "website": "www.ergs.sc.edu",
        "mission_statement": """<b>ERGS</b>, or <i>Energy Research Group: 
    Scopatz</i>, is the Computational 
    <a href="http://www.me.sc.edu/nuclear/">Nuclear Engineering</a>
    research group at the 
    <a href="http://sc.edu/">University of South Carolina</a>. 
    Our focus is on uncertainty quantification & predictive modeling, nuclear 
    fuel cycle simulation, and improving nuclear engineering techniques through 
    automation.
    We are committed to open & accessible research tools and methods.""",
        "projects": """ERGS is involved in a large number of computational 
    projects. Please visit the <a href="projects.html">projects page</a> for 
    more information!
    """,
        "email": "<b>scopatz</b> <i>(AT)</i> <b>cec.sc.edu</b>",
    },
    "institutions": [{
        "_id": "columbiau",
        "aka": ["Columbia University", "Columbia"],
        "city": "New York",
        "country": "USA",
        "day": 30,
        "departments": {
            "physics": {
                "name": "Department of Physics",
                "aka": ["Dept. of Physics", "Physics"],
            },
            "chemistry": {
                "name": "Department of Chemistry",
                "aka": ["Chemistry", "Dept. of Chemistry"],
            },
            "apam": {
                "name": "Department of Applied Physics " "and Applied Mathematics",
                "aka": ["APAM"],
            },
        },
        "month": "May",
        "name": "Columbia University",
        "schools": {
            "seas": {
                "name": "School of Engineering and " "Applied Science",
                "aka": [
                    "SEAS",
                    "Columbia Engineering",
                    "Fu Foundation School of Engineering " "and Applied Science",
                ],
            }
        },
        "state": "NY",
        "street": "500 W 120th St",
        "updated": "2020-05-30",
        "uuid": "avacazdraca345rfsvwre",
        "year": 2020,
        "zip": "10027",
    },
        {
            "_id": "usouthcarolina",
            "aka": ["The University of South Carolina"],
            "city": "Columbia",
            "country": "USA",
            "day": 30,
            "departments": {
                "physics": {
                    "name": "Department of Physics",
                    "aka": ["Dept. of Physics", "Physics"],
                },
                "chemistry": {
                    "name": "Department of Chemistry",
                    "aka": ["Chemistry", "Dept. of Chemistry"],
                },
                "apam": {
                    "name": "Department of Applied Physics" "and Applied Mathematics",
                    "aka": ["APAM"],
                },
                "mechanical engineering": {
                    "name": "Department of Mechanical Engineering",
                    "aka": ["Mechanical", "Dept. of Mechanical"],
                }
            },
            "month": "May",
            "name": "The University of South Carolina",
            "schools": {
                "cec": {
                    "name": "College of Engineering and" "Computing",
                    "aka": [
                        "CEC",
                        "College of Engineering and Computing",
                    ],
                }
            },
            "state": "SC",
            "street": "1716 College Street",
            "updated": "2020-06-30",
            "uuid": "4E89A0DD-19AE-45CC-BCB4-83A2D84545E3",
            "year": 2020,
            "zip": "29208",
        },
    ],
    "jobs": {
        "_id": "0004",
        "background_fields": [
            "Data Science",
            "Data Engineering",
            "Computer Engineering",
            "Computer Science",
            "Applied Mathematics",
            "Physics",
            "Nuclear Engineering",
            "Mechanical Engineering",
            "Or similar",
        ],
        "compensation": [
            "Salary and compensation will be based on prior work " "experience."
        ],
        "contact": "Please send CV or resume to Prof. Scopatz at "
                   "scopatzATcec.sc.edu.",
        "day": 1,
        "description": "<p>We are seeking a dedicated individual to "
                       "help to aid in ...",
        "month": "July",
        "open": False,
        "positions": ["Scientific Software Developer", "Programmer"],
        "start_date": "ASAP",
        "title": "Open Source Scientific Software Maintainer",
        "year": 2015,
    },
    "meetings": [{
        "_id": "grp2020-07-31",
        "actions": [
            "(Everyone) Update overdue milestones",
            "(Professor Billinge) Explore, and plan a machine learning project for DSI"
            "(Professor Billinge, Emil, Yevgeny, Songsheng) Come up with a Kaggle competition for this DSI project"
            "(Emil) Set up the slack channel for the DSI project"
        ],
        "agenda": ["Review actions","Fargo is not free on any streaming platforms","Review Airtable for deliverables and celebrate",
                   "Mention diversity action initiative","Songsheng's journal club presentation","(Vivian and Zicheng) Finish rest of crystallography presentation next week",
                   "Emil's 7th inning Yoga Stretch","Crystallography talk","Presentation"],
        "buddies": [
            "   Jaylyn C. Umana, "
            "   Simon J. L. Billinge",
            "   Long Yang, "
            "   Emil Kjaer",
            "   Sani Harouna-Mayer,"
            "   Akshay Choudhry",
            "   Vivian Lin, "
            "   Songsheng Tao",
            "   Ran Gu, "
            "   Adiba Ejaz",
            "   Zach Thatcher, "
            "   Yevgeny Rakita",
            "   Zicheng 'Taylor' Liu, "
            "   Eric Shen ",
            "   Hung Vuong, "
            "   Daniela Hikari Yano",
            "   Ahmed Shaaban, "
            "   Jiawei Zang",
            "   Berrak Ozer, "
            "   Michael Winitch",
            "   Shomik Ghose",
        ],
        "day": 31,
        "journal_club": {
            "doi": "10.1107/S2053273319005606",
            "presenter": "sbillinge",
        },
        "lead": "sbillinge",
        "minutes": [
            "Talked about eyesight and prescription lenses",
            "Professor Billinge tells everyone a Logician/Mathematician joke",
            "Mentioned pyjokes, a package in Python that lists bad jokes",
            "Jaylyn greets everyone",
            "Reviewed action items from last time",
            "Talked about fargo, and the merits (or lack thereof) of the Dakotas",
            "Celebrated finished prums",
            "Songhsheng holds journal club presentation on Machine Learning techniques",
            "Discussed Linear Classification, Gradient Descent, Perceptrons, Convolution and other ML topics",
            "Discussed how we can derive scientific meaning from ML algorithms",
            "Discussed real space versus reciprocal space",
            "Finished journal club, had to postpone Akshay's presentation, and the Yoga session to next week",
        ],
        "month": 7,
        "place": "Mudd 1106",
        "presentation": {
            "title": "PDF Distance Extraction",
            "link": "2007ac_grpmtg",
            "presenter": "sbillinge",
        },
        "scribe": "sbillinge",
        "time": '0',
        "updated": "2020-07-31 23:27:50.764475",
        "uuid": "3fbee8d9-e283-48e7-948f-eecfc2a123b7",
        "year": 2020

    },
        {
            "_id": "grp6000-01-01",
            "actions": [
                "Simon: test",
                "Everyone: Clear out-of-date prums milestones."
            ],
            "agenda": ["Review actions", ],
            "buddies": [],
            "day": 1,
            "journal_club": [],
            "lead": "scopatz",
            "minutes": [],
            "month": 1,
            "place": "Mudd 1106",
            "presentation": [],
            "scribe": "scopatz",
            "time": '0',
            "updated": "",
            "uuid": "",
            "year": 6000

        }
    ],
    "news": {
        "_id": "56b4eb6d421aa921504ef2a9",
        "author": "Anthony Scopatz",
        "body": "Dr. Robert Flanagan joined ERGS as a post-doctoral " "scholar.",
        "day": 1,
        "month": "February",
        "year": 2016,
    },
    "people": [{
        "_id": "scopatz",
        "aka": [
            "Scopatz",
            "Scopatz, A",
            "Scopatz, A.",
            "Scopatz, A M",
            "Anthony Michael Scopatz",
        ],
        "avatar": "https://avatars1.githubusercontent.com/u/320553?v" "=3&s=200",
        "appointments": {
            "f19": {
                "begin_year": 2019,
                "begin_month": 9,
                "begin_day": 1,
                "end_year": 2019,
                "end_month": 10,
                "end_day": 31,
                "grant": "dmref15",
                "type": "pd",
                "loading": 0.75,
                "status": "finalized",
                "notes": ["forgetmenot"]
            },
            "s20": {
                "begin_date": "2020-01-01",
                "end_date": "2020-05-15",
                "grant": "sym",
                "type": "pd",
                "loading": 1.0,
                "status": "finalized",
                "notes": ["fully appointed", "outdated grant"]
            },
            "ss20": {
                "begin_date": "2020-06-01",
                "end_date": "2020-08-31",
                "grant": "abc42",
                "type": "ss",
                "loading": 0.8,
                "status": "proposed",
                "notes": []
            }

        },
        "bio": "Anthony Scopatz is currently an Assistant Professor",
        "bios": ["Anthony Scopatz is currently an Assistant Professor but will go on to do great things"],
        "committees": [{
            "name": "Heather Stanford",
            "type": "phdoral",
            "year": 2020,
            "month": 3,
            "day": 1,
            "level": "department",
            "unit": "apam"
        },
            {"name": "Heather Stanford",
             "type": "promotion",
             "year": 2020,
             "month": 3,
             "day": 1,
             "level": "school",
             "unit": "seas"
             },
            {"name": "Heather Stanford",
             "type": "phddefense",
             "year": 2020,
             "month": 3,
             "day": 1,
             "notes": "something else to remember about it, not published",
             "level": "external",
             "unit": "U Denmark"
             },
            {"name": "Heather Stanford",
             "type": "promotion",
             "year": 2020,
             "month": 3,
             "day": 1,
             "unit": "columbiau",
             "level": "university",
             }],
        "education": [
            {
                "advisor": "ascopatz",
                "begin_year": 2008,
                "degree": "Ph.D. Mechanical Engineering, "
                          "Nuclear and Radiation Engineering "
                          "Program",
                "end_year": 2011,
                "group": "ergs",
                "institution": "The University of Texas at Austin",
                "department": "apam",
                "location": "Austin, TX",
                "other": [
                    "Adviser: Erich A. Schneider",
                    "Dissertation: Essential Physics for Fuel Cycle "
                    "Modeling & Analysis",
                ],
            },
            {
                "begin_year": 2006,
                "degree": "M.S.E. Mechanical Engineering, Nuclear and "
                          "Radiation Engineering Program",
                "end_year": 2007,
                "institution": "The University of Texas at Austin",
                "location": "Austin, TX",
                "other": [
                    "Adviser: Erich A. Schneider",
                    "Thesis: Recyclable Uranium Options under the Global "
                    "Nuclear Energy Partnership",
                ],
            },
            {
                "begin_year": 2002,
                "begin_month": "Sep",
                "begin_day": 1,
                "degree": "B.S. Physics",
                "end_year": 2006,
                "end_month": 5,
                "end_day": 20,
                "institution": "University of California, Santa Barbara",
                "location": "Santa Barbara, CA",
                "other": [
                    "Graduated with a Major in Physics and a Minor in " "Mathematics"
                ],
            },
            {
                "begin_year": 2008,
                "degree": "ongoing",
                "group": "life",
                "institution": "solar system",
                "department": "earth",
                "location": "land, mostly",
            },
        ],
        "email": "scopatz@cec.sc.edu",
        "employment": [
            {
                "advisor": "ascopatz",
                "begin_year": 2015,
                "coworkers": ["afriend"],
                "group": "ergs",
                "location": "Columbia, SC",
                "organization": "The University of South Carolina",
                "other": [
                    "Cyclus: An agent-based, discrete time nuclear fuel "
                    "cycle simulator.",
                    "PyNE: The Nuclear Engineering Toolkit.",
                    "Website: http://www.ergs.sc.edu/",
                ],
                "permanent": True,
                "position": "assistant professor",
                "position_full": "Assistant Professor, Mechanical Engineering " "Department",
            },
            {
                "begin_year": 2013,
                "begin_month": "Jun",
                "begin_day": 1,
                "end_year": 2015,
                "end_month": 3,
                "end_day": 15,
                "location": "Madison, WI",
                "organization": "CNERG, The University of " "Wisconsin-Madison",
                "department": "Physics",
                "other": [
                    "Cyclus: An agent-based, discrete time nuclear fuel "
                    "cycle simulator.",
                    "PyNE: The Nuclear Engineering Toolkit.",
                    "Website: https://cnerg.github.io/",
                ],
                "position": "associate scientist",
                "position_full": "Associate Scientist, Engineering Physics " "Department",
            },
            {
                "begin_day": 1,
                "begin_month": "Nov",
                "begin_year": 2011,
                "end_month": "May",
                "end_year": 2013,
                "location": "Chicago, IL",
                "organization": "The FLASH Center, The University of " "Chicago",
                "other": [
                    "NIF: Simulation of magnetic field generation from "
                    "neutral plasmas using FLASH.",
                    "CosmoB: Simulation of magnetic field generation "
                    "from neutral plasmas using FLASH.",
                    "FLASH4: High-energy density physics capabilities "
                    "and utilities.",
                    "Simulated Diagnostics: Schlieren, shadowgraphy, "
                    "Langmuir probes, etc. from FLASH.",
                    "OpacPlot: HDF5-based equation of state and opacity "
                    "file format.",
                    "Website: http://flash.uchicago.edu/site/",
                ],
                "position": "post-doctoral scholar",
                "position_full": "Research Scientist, Postdoctoral Scholar",
                "status": "pi"
            },
        ],
        "funding": [
            {
                "name": "Omega Laser User's Group Travel Award",
                "value": 1100,
                "year": 2013,
            },
            {"name": "NIF User's Group Travel Award", "value": 1150,
             "year": 2013},
        ],
        "google_scholar_url": "https://scholar.google.com/citations?user=dRm8f",
        "github_id": "ascopatz",
        "hindex": [{
            "h": 25,
            "h_last_five": 46,
            "citations": 19837,
            "citations_last_five": 9419,
            "origin": "Google Scholar",
            "since": 1991,
            "year": 2020,
            "month": 2,
            "day": 19
        }],
        "home_address": {
            "street": "123 Wallabe Ln",
            "city": "The big apple",
            "state": "plasma",
            "zip": "007",
        },
        "initials": "AMS",
        "membership": [
            {
                "begin_year": 2006,
                "organization": "American Nuclear Society",
                "position": "Member",
            },
            {
                "begin_year": 2013,
                "organization": "Python Software Foundation",
                "position": "Fellow",
            },
        ],
        "name": "Anthony Scopatz",
        "orcid_id": "0000-0002-9432-4248",
        "position": "professor",
        "research_focus_areas": [
            {"begin_year": 2010, "description": "software applied to nuclear "
                                                "engineering and life"}
        ],
        "service": [{
            "name": "International Steering Committee",
            "role": "chair",
            "type": "profession",
            "year": 2020,
            "month": 3,
            "notes": ["something"],
        }, {
            "name": "National Steering Committee",
            "type": "profession",
            "begin_year": 2018,
            "end_year": 2021,
            "notes": "something",
        },
        ],
        "skills": [
            {"category": "Programming Languages", "level": "expert",
             "name": "Python"},
            {"category": "Programming Languages", "level": "expert",
             "name": "Cython"},
        ],
        "teaching": [
            {
                "course": "EMCH 552: Intro to Nuclear Engineering",
                "courseid": "EMCH 552",
                "description": "This course is an introduction to nuclear " "physics.",
                "enrollment": "tbd",
                "month": "August",
                "organization": "University of South Carolina",
                "position": "professor",
                "semester": "Spring",
                "syllabus": "https://drive.google.com/open?id"
                            "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                "year": 2017,
            },
            {
                "course": "EMCH 558/758: Reactor Power Systems",
                "courseid": "EMCH 558",
                "description": "This course covers conventional " "reactors.",
                "enrollment": 28,
                "evaluation": {
                    "response_rate": 66.76,
                    "amount_learned": 3.5,
                    "appropriateness_workload": 3.15,
                    "course_overall": 3.67,
                    "fairness_grading": 3.54,
                    "organization": 3.25,
                    "classroom_delivery": 4,
                    "approachability": 4.3,
                    "instructor_overall": 3.5,
                    "comments": ["super duper", "dandy"]
                },
                "month": "January",
                "organization": "University of South Carolina",
                "position": "professor",
                "syllabus": "https://docs.google.com/document/d"
                            "/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8"
                            "-PxiboYdM/edit?usp=sharing",
                "year": 2017,
            },
        ],
        "title": "Dr.",
    },
        {
            "_id": "sbillinge",
            "active": True,
            "activities": [{
                "type": "teaching",
                "name": "course development",
                "year": 2018,
                "other": "Developed a new course for Materials Science"
            }],
            "aka": [
                "Billinge",
            ],
            "avatar": "https://avatars1.githubusercontent.com/u/320553?v" "=3&s=200",
            "bio": "Simon teaches and does research",
            "committees": [{
                "name": "Same Old",
                "type": "phddefense",
                "year": 2018,
                "unit": "Materials Science",
                "level": "department",
                "notes": "something"
            }],
            "education": [
                {
                    "begin_year": 2008,
                    "degree": "Ph.D. Mechanical Engineering, "
                              "Nuclear and Radiation Engineering "
                              "Program",
                    "end_year": 2011,
                    "group": "ergs",
                    "institution": "The University of Texas at Austin",
                    "department": "apam",
                    "location": "Austin, TX",
                    "other": [
                        "Adviser: Erich A. Schneider",
                        "Dissertation: Essential Physics for Fuel Cycle "
                        "Modeling & Analysis",
                    ],
                },
            ],
            "email": "sb2896@columbia.edu",
            "employment": [
                {
                    "begin_year": 2015,
                    "group": "ergs",
                    "location": "Columbia, SC",
                    "organization": "The University of South Carolina",
                    "other": [
                        "Cyclus: An agent-based, discrete time nuclear fuel "
                        "cycle simulator.",
                        "PyNE: The Nuclear Engineering Toolkit.",
                        "Website: http://www.ergs.sc.edu/",
                    ],
                    "position": "assistant professor",
                },
            ],
            "facilities": [{
                "type": "other",
                "name": "Shared {Habanero} compute cluster",
                "begin_year": 2015
            },
                {
                    "type": "research_wish",
                    "name": "Shared access to wet lab",
                    "begin_year": 2015
                },
                {
                    "type": "teaching",
                    "name": "Courseworks2",
                    "begin_year": 2017
                },
                {
                    "type": "teaching_wish",
                    "name": "nothing right now",
                    "begin_year": 2019
                },
                {
                    "type": "research",
                    "name": "I don't have one",
                    "begin_year": 2008
                },
            ],
            "funding": [
                {
                    "name": "Omega Laser User's Group Travel Award",
                    "value": 1100,
                    "year": 2013,
                },
                {"name": "NIF User's Group Travel Award", "value": 1150,
                 "year": 2013},
            ],
            "google_scholar_url": "https://scholar.google.com/citations?user=dRm8f",
            "hindex": [{
                "h": 65,
                "h_last_five": 43,
                "citations": 17890,
                "citations_last_five": 8817,
                "origin": "Google Scholar",
                "since": 1991,
                "year": 2019,
                "month": "May",
                "day": 12,
            }],
            "office": "1105 Seely W. Mudd Building (inner office)",
            "home_address": {
                "street": "123 Wallabe Ln",
                "city": "The big apple",
                "state": "plasma",
                "zip": "007",
            },
            "initials": "SJLB",
            "membership": [
                {
                    "begin_year": 2006,
                    "organization": "American Nuclear Society",
                    "position": "Member",
                },
            ],
            "miscellaneous": {
                "metrics_for_success": [
                    "publications(quality, quantity)",
                    "invite talks",
                    "funding",
                    "citations",
                ],
            },
            "name": "Simon J. L. Billinge",
            "orcid_id": "0000-0002-9432-4248",
            "position": "professor",
            "publicity": [{
                "type": "online",
                "publication": "Brookhaven National Laboratory Web Story",
                "topic": "LDRD Provenance project",
                "title": "An awesome project and well worth the money",
                "day": 24,
                "month": "Jul",
                "year": 2019,
                "grant": "bnlldrd18",
                "url": "http://www.google.com"
            },
            ],
            "research_focus_areas": [
                {"begin_year": 2010, "description": "software applied to materials "
                                                    "engineering and life"}
            ],
            "service": [
                {
                    "type": "profession",
                    "name": "Master of Ceremonies and Organizer Brown University "
                            '"Chemistry: Believe it or Not" public chemistry '
                            "demonstration",
                    "year": 2017,
                    "month": "August"
                },
                {
                    "type": "department",
                    "name": "Applied Physics program committee",
                    "year": 2018,
                    "month": 1
                },
                {
                    "type": "school",
                    "name": "Ad hoc tenure committee",
                    "year": 2017,
                    "month": 6,
                    "notes": "Albert Einstein"
                },
                {
                    "type": "profession",
                    "name": "Co-organizer JUAMI",
                    "year": 2017,
                    "month": 12,
                    "role": "co-organizer",
                    "other": "great way to meet people",
                },
            ],
            "skills": [
                {"category": "Programming Languages", "level": "expert",
                 "name": "Python"},
            ],
            "teaching": [
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "f17-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "evaluation": {
                        "response_rate": 58.33,
                        "amount_learned": 4.57,
                        "appropriateness_workload": 4.29,
                        "fairness_grading": 4.57,
                        "course_overall": 4.43,
                        "organization": 4.0,
                        "classroom_delivery": 4.29,
                        "approachability": 4.86,
                        "instructor_overall": 4.43,
                        "comments": [
                            "Great teacher but disorganized",
                            "Wears pink pants.  Why?",
                        ]},
                    "month": "August",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Fall",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2016,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "f17-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "evaluation": {
                        "response_rate": 58.33,
                        "amount_learned": 4.57,
                        "appropriateness_workload": 4.29,
                        "fairness_grading": 4.57,
                        "course_overall": 4.43,
                        "organization": 4.0,
                        "classroom_delivery": 4.29,
                        "approachability": 4.86,
                        "instructor_overall": 4.43,
                        "comments": [
                            "Great teacher but disorganized",
                            "Wears pink pants.  Why?",
                        ]},
                    "month": "August",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Fall",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2017,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "s17-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "evaluation": {
                        "response_rate": 58.33,
                        "amount_learned": 4.57,
                        "appropriateness_workload": 4.29,
                        "fairness_grading": 4.57,
                        "course_overall": 4.43,
                        "organization": 4.0,
                        "classroom_delivery": 4.29,
                        "approachability": 4.86,
                        "instructor_overall": 4.43,
                        "comments": [
                            "Great teacher but disorganized",
                            "Wears pink pants.  Why?",
                        ]},
                    "month": "Jan",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Spring",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2018,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "s17-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "evaluation": {
                        "response_rate": 58.33,
                        "amount_learned": 4.57,
                        "appropriateness_workload": 4.29,
                        "fairness_grading": 4.57,
                        "course_overall": 4.43,
                        "organization": 4.0,
                        "classroom_delivery": 4.29,
                        "approachability": 4.86,
                        "instructor_overall": 4.43,
                        "comments": [
                            "Great teacher but disorganized",
                            "Wears pink pants.  Why?",
                        ]},
                    "month": "Jan",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Spring",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2017,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "s17-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "month": "Jan",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Spring",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2019,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "f18-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "enrollment": 18,
                    "evaluation": {
                        "response_rate": 58.33,
                        "amount_learned": 4.57,
                        "appropriateness_workload": 4.29,
                        "fairness_grading": 4.57,
                        "course_overall": 4.43,
                        "organization": 4.0,
                        "classroom_delivery": 4.29,
                        "approachability": 4.86,
                        "instructor_overall": 4.43,
                        "comments": [
                            "Great teacher but disorganized",
                            "Wears pink pants.  Why?",
                        ]},
                    "month": "August",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Fall",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2018,
                },
                {
                    "course": 'MSAE-3010: Introduction to Materials Science',
                    "courseid": "f19-3010",
                    "description": "This course is an introduction to nuclear " "physics.",
                    "month": "August",
                    "organization": "Columbia University",
                    "position": "professor",
                    "semester": "Fall",
                    "syllabus": "https://drive.google.com/open?id"
                                "=0BxUpd34yizZreDBCMEJNY2FUbnc",
                    "year": 2019,
                },
            ],
            "title": "Dr.",
            "todos": [
                {"description": "read paper",
                 "due_date": "2020-07-19",
                 "begin_date": "2020-06-15",
                 "duration": 60.0,
                 "importance": 2,
                 "status": "started",
                 "assigned_by": "scopatz",
                 "running_index": 1
                 },
                {"description": "prepare the presentation",
                 "due_date": "2020-07-29",
                 "begin_date": "2020-06-22",
                 "duration": 30.0,
                 "importance": 0,
                 "status": "started",
                 "notes": ["about 10 minutes", "don't forget to upload to the website"],
                 "assigned_by": "sbillinge",
                 "running_index": 2
                 }
            ],
        },
        {"_id": "abeing",
         "active": False,
         "aka": ["being", "human", "person"],
         "avatar": "https://xkcd.com/1221/",
         "bio": "Abstract Being is an exemplar human existence",
         "education": [
             {"degree": "bachelors", "institution": "University of Laughs", "begin_year": 2010},
         ],
         "employment": [
             {"group": "bg", "begin_date": "2015-06-01", "end_date": "2015-08-31", "organization": "columbiau",
              "position": "intern"},
             {"group": "agroup", "begin_date": "2020-01-01", "end_date": "2030-12-31", "organization": "usouthcarolina",
              "position": "intern"},
             {"group": "bg", "begin_date": "2010-06-01", "end_date": "2012-08-31", "organization": "columbiau",
              "position": "intern"},
             {"group": "bg", "begin_date": "2017-06-01", "end_date": "2019-08-31", "organization": "columbiau",
              "position": "intern"},
         ],
         "position": "intern",
         "name": "Abstract Being",
         }
    ],
    "presentations": [
        {
            "_id": "18sb_this_and_that",
            "abstract": "We pulled apart graphite with tape",
            "authors": ["scopatz"],
            "begin_year": 2018,
            "begin_month": 5,
            "begin_day": 22,
            "department": "apam",
            "institution": "columbiau",
            "location": "Upton NY",
            "meeting_name": "Meeting to check flexibility on dates",
            "notes": [
                "We hope the weather will be sunny",
                "if the weather is nice we will go to the " "beach",
            ],
            "project": "18sob_clustermining",
            "status": "accepted",
            "title": "Graphitic Dephenestration",
            "type": "award",
            "webinar": False,
        },
        {
            "_id": "18sb_nslsii",
            "abstract": "We pulled apart graphite with tape",
            "authors": ["scopatz"],
            "begin_year": 2018,
            "begin_month": 5,
            "begin_day": 22,
            "department": "apam",
            "end_year": 2018,
            "end_month": 5,
            "end_day": 22,
            "institution": "columbiau",
            "location": "Upton NY",
            "meeting_name": "2018 NSLS-II and CFN Users Meeting",
            "notes": [
                "We hope the weather will be sunny",
                "if the weather is nice we will go to the " "beach",
            ],
            "project": "18sob_clustermining",
            "status": "accepted",
            "title": "ClusterMining: extracting core structures of "
                     "metallic nanoparticles from the atomic pair "
                     "distribution function",
            "type": "poster",
        },
        {
            "_id": "18sb04_kentstate",
            "abstract": "We made the case for local structure",
            "authors": ["scopatz"],
            "begin_year": 2018,
            "begin_month": "May",
            "begin_day": 22,
            "department": "physics",
            "end_year": 2018,
            "end_month": 5,
            "end_day": 22,
            "institution": "columbiau",
            "notes": ["what a week!"],
            "project": "18kj_conservation",
            "status": "accepted",
            "title": "Nanostructure challenges and successes from "
                     "16th Century warships to 21st Century energy",
            "type": "colloquium",
            "webinar": True,
        },
    ],
    "projecta": {
        "_id": "20sb_firstprojectum",
        "begin_date": "2020-04-28",
        "collaborators": ["aeinstein", "pdirac"],
        "deliverable": {
            "audience": ["beginning grad in chemistry"],
            "due_date": "2021-05-05",
            "success_def": "audience is happy",
            "scope": ["UCs that are supported or some other scope description "
                      "if it is software", "sketch of science story if it is paper"
                      ],
            "platform": "description of how and where the audience will access "
                        "the deliverable.  Journal if it is a paper",
            "roll_out": [
                "steps that the audience will take to access and interact with "
                "the deliverable", "not needed for paper submissions"],
            "status": "finalized"
        },
        "description": "My first projectum",
        "end_date": "2020-06-05",
        "grants": "SymPy-1.1",
        "group_members": ["ascopatz"],
        "kickoff": {
            "date": "2020-05-05",
            "due_date": "2020-05-06",
            "name": "Kick off meeting",
            "objective": "introduce project to the lead",
            "audience": ["lead", "pi", "group_members"],
            "status": "finished"
        },
        "lead": "ascopatz",
        "log_url": "https://docs.google.com/document/d/1YC_wtW5Q",
        "milestones": [{
            'due_date': '2020-05-20',
            'name': 'Project lead presentation',
            'objective': 'lead presents background reading and '
                         'initial project plan',
            'audience': ['lead', 'pi', 'group_members'],
            'status': 'proposed',
            'type': 'meeting'
        },
            {'due_date': '2020-05-27',
             'name': 'planning meeting',
             'objective': 'develop a detailed plan with dates',
             'audience': ['lead', 'pi', 'group_members'],
             'status': 'proposed',
             'type': 'pr',
             }],
        "name": "First Projectum",
        "pi_id": "scopatz",
        "status": "proposed"
    },
    "projects": {
        "_id": "Cyclus",
        "name": "Cyclus",
        "description": "Agent-Based Nuclear Fuel Cycle Simulator",
        "group": "ergs",
        "highlights": [
            {"year": 2020, "month": 5,
             "description": "high profile pub in Nature"}
        ],
        "logo": "http://fuelcycle.org/_static/big_c.png",
        "other": [
            "Discrete facilities with discrete material transactions",
            "Low barrier to entry, rapid payback to adoption",
        ],
        "repo": "https://github.com/cyclus/cyclus/",
        "team": [
            {
                "begin_month": "June",
                "begin_year": 2013,
                "end_month": "July",
                "end_year": 2015,
                "name": "Anthony Scopatz",
                "position": "Project Lead",
            }
        ],
        "type": "funded",
        "website": "http://fuelcycle.org/",
        "grant": "dmref15",
    },
    "proposalReviews": [
        {
            "_id": "1906doeExample",
            "adequacy_of_resources": [
                "The resources available to the PI seem adequate"
            ],
            "agency": "doe",
            "competency_of_team": ["super competent!"],
            "doe_appropriateness_of_approach": [
                "The proposed approach is highly innovative"
            ],
            "doe_reasonableness_of_budget": [
                "They could do it with half the money"],
            "doe_relevance_to_program_mission": ["super relevant"],
            "does_how": [
                "they will find the cause of Malaria",
                "when they find it they will determine a cure",
            ],
            "due_date": "2020-04-10",
            "does_what": "Find a cure for Malaria",
            "freewrite": [
                "I can put extra things here, such as special instructions from the",
                "program officer",
            ],
            "goals": [
                "The goals of the proposal are to put together a team to find a cure"
                "for Malaria, and then to find it"
            ],
            "importance": ["save lives", "lift people from poverty"],
            "institutions": "columbiau",
            "month": "May",
            "names": ["B. Cause", "A.N. Effect"],
            "nsf_broader_impacts": [],
            "nsf_create_original_transformative": [],
            "nsf_plan_good": [],
            "nsf_pot_to_advance_knowledge": [],
            "nsf_pot_to_benefit_society": [],
            "requester": "Lane Wilson",
            "reviewer": "sbillinge",
            "status": "submitted",
            "summary": "dynamite proposal",
            "title": "A stunning new way to cure Malaria",
            "year": 2019,
        },
        {
            "_id": "1906nsfExample",
            "adequacy_of_resources": [
                "The resources available to the PI seem adequate"
            ],
            "agency": "nsf",
            "competency_of_team": ["super competent!"],
            "doe_appropriateness_of_approach": [],
            "doe_reasonableness_of_budget": [],
            "doe_relevance_to_program_mission": [],
            "does_how": [
                "they will find the cause of Poverty",
                "when they find it they will determine a cure",
            ],
            "does_what": "Find a cure for Poverty",
            "due_date": "2020-04-10",
            "freewrite": [
                "I can put extra things here, such as special instructions from the",
                "program officer",
            ],
            "goals": [
                "The goals of the proposal are to put together a team to find a cure"
                "for Poverty, and then to find it"
            ],
            "importance": ["save lives", "lift people from poverty"],
            "institutions": "upenn",
            "month": "May",
            "names": ["A Genius"],
            "nsf_broader_impacts": ["Poor people will be made unpoor"],
            "nsf_create_original_transformative": [
                "transformative because lives will be transformed"
            ],
            "nsf_plan_good": [
                "I don't see any issues with the plan",
                "it should be very straightforward",
            ],
            "nsf_pot_to_advance_knowledge": [
                "This won't advance knowledge at all"],
            "nsf_pot_to_benefit_society": [
                "Society will benefit by poor people being made unpoor if they want "
                "to be"
            ],
            "requester": "Tessemer Guebre",
            "reviewer": "sbillinge",
            "status": "submitted",
            "summary": "dynamite proposal",
            "title": "A stunning new way to cure Poverty",
            "year": 2019,
        },
    ],
    "proposals": [
        {
            "_id": "mypropsal",
            "amount": 1000000.0,
            "authors": ["Anthony Scopatz", "Robert Flanagan"],
            "begin_day": 1,
            "begin_month": "May",
            "begin_year": 2030,
            "currency": "USD",
            "day": 18,
            "duration": 3,
            "end_day": 31,
            "end_month": "December",
            "end_year": 2030,
            "full": {
                "benefit_of_collaboration": "http://pdf.com"
                                            "/benefit_of_collaboration",
                "cv": ["http://pdf.com/scopatz-cv",
                       "http://pdf.com/flanagan-cv"],
                "narrative": "http://some.com/pdf",
            },
            "month": "Aug",
            "notes": "Quite an idea",
            "pi": "Anthony Scopatz",
            "pre": {
                "benefit_of_collaboration": "http://pdf.com"
                                            "/benefit_of_collaboration",
                "cv": ["http://pdf.com/scopatz-cv",
                       "http://pdf.com/flanagan-cv"],
                "day": 2,
                "month": "Aug",
                "narrative": "http://some.com/pdf",
                "year": 1998,
            },
            "status": "submitted",
            "title": "A very fine proposal indeed",
            "year": 1999,
        },
        {
            "_id": "dmref15",
            "amount": 982785.0,
            "authors": ["qdu", "dhsu", "sbillinge"],
            "call_for_proposals": "http://www.nsf.gov/pubs/2014/nsf14591/"
                                  "nsf14591.htm",
            "begin_day": 1,
            "begin_month": "May",
            "begin_year": 2018,
            "cpp_info": {
                "cppflag": True,
                "other_agencies_submitted": "None",
                "institution": "Columbia University",
                "person_months_academic": 0,
                "person_months_summer": 1,
                "project_scope": "lots to do but it doesn't overlap with any "
                                 "other of my grants"
            },
            "currency": "USD",
            "day": 2,
            "duration": 3,
            "end_day": 1,
            "end_month": "May",
            "end_year": 2019,
            "funder": "NSF",
            "month": "february",
            "notes": "Quite an idea",
            "pi": "Simon Billinge",
            "status": "accepted",
            "team": [
                {
                    "institution": "Columbia University",
                    "name": "qdu",
                    "position": "co-pi",
                },
                {
                    "institution": "Columbia University",
                    "name": "dhsu",
                    "position": "co-pi",
                },
                {
                    "institution": "Columbia University",
                    "name": "sbillinge",
                    "position": "pi",
                    "subaward_amount": 330000.0,
                },
            ],
            "title": "DMREF: Novel, data validated, nanostructure determination "
                     "methods for accelerating materials discovery",
            "title_short": "DMREF nanostructure",
            "year": 2015,
        },
        {
            "_id": "SymPy-1.1",
            "amount": 3000.0,
            "begin_date": "2030-05-01",
            "end_date": "2030-12-31",
            "cpp_info": {
                "cppflag": True,
                "other_agencies_submitted": "None",
                "institution": "Columbia University",
                "person_months_academic": 0,
                "person_months_summer": 1,
                "project_scope": ""
            },
            "currency": "USD",
            "pi": "sbillinge",
            "status": "submitted",
            "title": "SymPy 1.1 Release Support",
        },
        {
            "_id": "SymPy-2.0",
            "amount": 3000.0,
            "begin_date": "2019-06-01",
            "end_date": "2030-12-31",
            "cpp_info": {
                "cppflag": True,
                "other_agencies_submitted": "None",
                "institution": "Columbia University",
                "person_months_academic": 0,
                "person_months_summer": 1,
                "project_scope": ""
            },
            "currency": "USD",
            "pi": "sbillinge",
            "status": "submitted",
            "title": "SymPy 1.1 Release Support",
        },
        {
            "_id": "abc42",
            "amount": 42000.0,
            "begin_date": "2020-06-01",
            "end_date": "2020-12-31",
            "cpp_info": {
                "cppflag": True,
                "other_agencies_submitted": "None",
                "institution": "Columbia University",
                "person_months_academic": 0,
                "person_months_summer": 1,
                "project_scope": ""
            },
            "currency": "USD",
            "pi": "sbillinge",
            "status": "submitted",
            "title": "The answer to life, the universe, and everything",
        }
    ],
    "reading_lists": {
        "_id": "getting_started_with_pdf",
        "day": "15",
        "month": "12",
        "papers": [{"doi": "10.1107/97809553602060000935",
                    "text": "Very basic, but brief, intro to powder diffraction in general"},
                   {"doi": "10.1039/9781847558237-00464",
                    "text": "Lightest weight overview of PDF analysis around.  Good starting point"
                    },
                   {"url": "http://www.diffpy.org",
                    "text": "Download and install PDFgui software and run through the step by step tutorial under the help tab"}
                   ],
        "purpose": "Beginning reading about PDF",
        "title": "A step-by-step pathway towards PDF understanding.  It is recommended to read the papers in the order they are listed here.",
        "year": 2019,
    },
    "refereeReports": {
        "_id": "1902nature",
        "claimed_found_what": ["gravity waves"],
        "claimed_why_important": ["more money for ice cream"],
        "did_how": ["measured with a ruler"],
        "did_what": ["found a much cheaper way to measure gravity waves"],
        "due_date": '2020-04-11',
        "editor_eyes_only": "to be honest, I don't believe a word of it",
        "final_assessment": ["The authors should really start over"],
        "first_author_last_name": "Wingit",
        "freewrite": "this comment didn't fit anywhere above",
        "journal": "Nature",
        "recommendation": "reject",
        "requester": "Max Planck",
        "reviewer": "sbillinge",
        "status": "submitted",
        "submitted_date": "2019-01-01",
        "title": "a ruler approach to measuring gravity waves",
        "validity_assessment": ["complete rubbish"],
        "year": 2019,
    },
    "students": {
        "_id": "Human A. Person",
        "aka": ["H. A. Person"],
        "email": "haperson@uni.edu",
        "university_id": "HAP42",
    },

}

SCHEMAS = {
    "abstracts": {
        "_description": {
            "description": "Abstracts for a conference or workshop. This is "
                           "generally public information"
        },
        "_id": {
            "description": "Unique identifier for submission. This generally "
                           "includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "coauthors": {
            "description": "names of coauthors",
            "required": False,
            "type": "string",
        },
        "email": {
            "description": "contact email for the author.",
            "required": True,
            "type": "string",
        },
        "firstname": {
            "description": "first name of the author.",
            "required": True,
            "type": "string",
        },
        "institution": {
            "description": "name of the institution",
            "required": True,
            "type": "string",
        },
        "lastname": {
            "description": "last name of the author.",
            "required": True,
            "type": "string",
        },
        "references": {
            "description": "HTML string of reference for the abstract itself",
            "required": False,
            "type": "string",
        },
        "text": {
            "description": "HTML string of the abstract.",
            "required": True,
            "type": "string",
        },
        "timestamp": {
            "description": "The time when the abstract was submitted.",
            "required": True,
            "type": "string",
        },
        "title": {
            "description": "title of the presentation/paper.",
            "required": True,
            "type": "string",
        },
    },
    "assignments": {
        "_description": {
            "description": "Information about assignments for classes."},
        "_id": {
            "description": "A unique id for the assignment, such as "
                           "HW01-EMCH-558-2016-S",
            "required": True,
            "type": "string",
        },
        "category": {
            "description": "such as 'homework' or 'final'",
            "required": True,
            "type": "string",
        },
        "courses": {
            "description": "ids of the courses that have this assignment",
            "required": True,
            "anyof_type": ["string", "list"],
        },
        "file": {
            "description": "path to assignment file in store",
            "required": False,
            "type": "string",
        },
        "points": {
            "description": "list of number of points possible for each "
                           "question. Length is the number of questions",
            "required": True,
            "type": "list",
            "schema": {"anyof_type": ["integer", "float"]},
        },
        "questions": {
            "description": "titles for the questions on this assignment",
            "required": False,
            "type": "list",
        },
        "solution": {
            "description": "path to solution file in store",
            "required": False,
            "type": "string",
        },
    },
    "beamplan": {
        "_id": {
            "description": "Unique identifier for the experiment plan. It should have a format '{year:2d}{month:2d}{people_id:s}_{plan_name:s}'",
            "required": True,
            "type": "string"
        },
        "_description": {
            "description": "Information about the experiment plan for the beamtime."},
        "project_lead": {
            "description": "The id for person who put out this plan. It should be inside the people.yml.",
            "required": True,
            "type": "string"
        },
        "project": {
            "description": "The id for the project which the plan belongs to. It should be on airtable.",
            "required": True,
            "type": "string"
        },
        "begin_date": {
            "description": "The begin date of the beam time.",
            "required": True,
            "anyof_type": ["string", "datetime", "date"]
        },
        "end_date": {
            "description": "The end date of the beam time.",
            "required": True,
            "anyof_type": ["string", "datetime", "date"]
        },
        "beamtime": {
            "description": "The id for the beamtime. Check the Airtable.",
            "required": True,
            "type": "string"
        },
        "holder": {
            "description": "Sample holder used during the measurement, e. g. 3 mm OD tubes holder.",
            "required": True,
            "type": "string"
        },
        "devices": {
            "description": "The dictionary of devices used in the measurement e. g. ",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "measurement": {
            "description": "What data to be measured, e. g. PDF, XRD, SAXS. This will determine the setup.",
            "required": True,
            "type": "string"
        },
        "samples": {
            "description": "The list of samples to be measured.",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "time": {
            "description": "The total time of executing the exp_plan. Unit: min.",
            "required": True,
            "type": "integer"
        },
        "objective": {
            "description": "What to study in the experiments. What goal to achieve.",
            "required": True,
            "type": "string"
        },
        "prep_plan": {
            "description": "Steps to prepare the samples. Do NOT need details.",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "ship_plan": {
            "description": "Steps to carry the samples from the producer to the BNL. Do NOT need details.",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "exp_plan": {
            "description": "Steps to carry out the experiments at BNL. Need details",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "scanplan": {
            "description": "The scanplan for the experiment, e. g. tseries, Tramp, ct.",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "pipeline": {
            "description": "The analysis pipeline for the experiment. If no new pipeline is needed, use 'usual'.",
            "required": True,
            "type": "string",
            "default": "usual"
        },
        "todo": {
            "description": "The TODO list before the beamtime.",
            "required": True,
            "type": "list",
            "schema": {
                "type": "string"
            }
        },
        "notes": {
            "description": "Notes of the plan, e. g. the preferred time.",
            "required": False,
            "anyof_type": [
                "list",
                "string"
            ],
            "schema": {
                "type": "string"
            }
        }
    },
    "blog": {
        "_description": {
            "description": "This collection represents blog posts written by "
                           "the members of the research group."
        },
        "_id": {
            "description": "short representation, such as this-is-my-title",
            "required": True,
            "type": "string",
        },
        "author": {
            "description": "name or AKA of author",
            "required": True,
            "type": "string",
        },
        "day": {"description": "Publication day", "required": True,
                "type": "integer"},
        "month": {
            "description": "Publication month",
            "required": True,
            "anyof_type": ["string", "integer"],
        },
        "original": {
            "description": "URL of original post, if this is a repost",
            "required": False,
            "type": "string",
        },
        "post": {
            "description": "actual contents of the post",
            "required": True,
            "type": "string",
        },
        "title": {
            "description": "full human readable title",
            "required": True,
            "type": "string",
        },
        "year": {
            "description": "Publication year",
            "required": True,
            "type": "integer",
        },
    },
    "contacts": {
        "_description": {"description": "a lighter version of people.  Fewer required fields"
                                        "for capturing people who are less tightly coupled"
                         },
        "_id": {
            "description": "id of the person, e.g., first letter first name "
                           "plus last name, but unique",
            "required": True,
        },
        "aka": {
            "required": False,
            "type": "list",
            "description": "other names for the person",
        },
        "date": {
            "description": "date when the entry was created in ISO format",
            "required": False,
            "anyof_type": ["string", "date"],
        },
        'day': {
            "description": "day when the entry was created",
            "required": False,
            "type": "integer",
        },
        "department": {
            "description": "Department at the institution",
            "type": "string",
            "required": False,
        },
        "email": {
            "description": "Contact email for the contact",
            "type": "string",
            "required": False,
        },
        "institution": {
            "description": "the institution where they are located.  This is"
                           "required for building a COI list of coauthors, but"
                           "not in general.  It can be institute id or anything"
                           "in the aka or name",
            "required": False,
            "type": "string"
        },
        'month': {
            "description": "month when the entry was created",
            "required": False,
            "anyof_type": ["string", "integer"],
        },
        "name": {
            "description": "the person's canonical name",
            "required": True,
            "type": "string",
        },
        "notes": {
            "description": "notes about the person",
            "required": False,
            "anyof_type": ["list", "string"]
        },
        "title": {
            "description": "how the person is addressed",
            "required": False,
            "type": "string",
        },
        'updated': {
            "description": "most recently updated",
            "required": False,
            "anyof_type": ["string", "datetime", "date"],
        },
        'year': {
            "description": "year when the entry was created",
            "required": False,
            "type": "integer",
        },
        'uuid': {
            "description": "universally unique identifier",
            "required": False,
            "type": "string",
        },
    },
    "expenses": {
        "_description": {
            "description": "This collection records expenses for the "
                           "group. It should most likely be private"
        },
        "_id": {
            "description": "short representation, such as this-is-my-name",
            "required": True,
            "type": "string",
        },
        "begin_date": {
            "description": "begin date in YYYY-MM-DD",
            "anyof_type": ["string", "date"],
        },
        "end_date": {
            "description": "end date in YYYY-MM-DD",
            "anyof_type": ["string", "date"],

        },
        "grant_percentages": {
            "description": "the percentage of the reimbursement amount to put "
                           "on each grant. This list must be the same length as"
                           "the grants list and the percentages placed in the "
                           "order that the grants appear in that list",
            "required": False,
            "type": "list",
        },
        "grants": {
            "description": "the grants in a list, or a string if only one grant",
            "required": True,
            "anyof_type": ["string", "list"],
        },
        "project": {
            "description": "project or list of projects that this "
                           "presentation is associated with.  Should "
                           "be discoverable in projects collection",
            "anyof_type": ["string", "list"],
        },
        "payee": {
            "description": "The name or id of the payee filing the expense",
            "required": True,
            "type": "string",
        },
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": False,
                        "type": "integer",
                    },
                    "date": {
                        "description": "Expense date",
                        "required": False,
                        "anyof_type": ["string", "date"],
                    },
                    "month": {
                        "description": "Expense month",
                        "required": False,
                        "anyof_type": ["string", "integer"],
                    },
                    "year": {
                        "description": "Expense year",
                        "required": False,
                        "type": "integer",
                    },
                    "purpose": {
                        "description": "reason for expense",
                        "type": "string",
                        "required": True,
                    },
                    "unsegregated_expense": {
                        "description": "The allowed expenses",
                        "type": "float",
                    },
                    "segregated_expense": {
                        "description": "The unallowed expenses",
                        "type": "float",
                    },
                    "original_currency": {
                        "description": "The currency the payment was made in",
                        "type": "float",
                    },
                },
            },
        },
        "overall_purpose": {
            "description": "The reason for the expenses",
            "type": "string",
            "required": True,
        },
        "notes": {
            "description": "Notes about the expense",
            "type": "list",

        },
        "status": {
            "description": "The status of the expense",
            "eallowed": ["reimbursed", "submitted", "unsubmitted", ],
            "type": "string"
        },
        "reimbursements": {
            "description": "Reimbursements for the expense",
            "schema": {
                "schema": {
                    'amount': {"description": 'amount for reimbursements',
                               "type": "float",
                               },
                    'date': {"description": "date of reimbursement",
                             "anyof_type": ["string", "date"],
                             },
                    'submission_date': {"description": "date of submission",
                                        "anyof_type": ["string", "date"],
                                        },
                    'submission_day': {"description": "day of submission. deprecated but here for "
                                                      "backwards compatibility",
                                       "type": "integer",
                                       },
                    'submission_month': {"description": "month of submission. deprecated but here for "
                                                        "backwards compatibility",
                                         "anyof_type": ["integer", "string"],
                                         },
                    'submission_year': {"description": "year of submission. deprecated but here for "
                                                       "backwards compatibility",
                                        "type": "integer",
                                        },
                    'day': {"description": "day of reimbursement. deprecated but here for "
                                           "backwards compatibility",
                            "type": "integer",
                            },
                    'month': {"description": "month of reimbursement. deprecated but here for "
                                             "backwards compatibility",
                              "anyof_type": ["string", "integer"],
                              },
                    'year': {"description": "year of reimbursement. deprecated but here for "
                                            "backwards compatibility",
                             "type": "integer",
                             },
                    'where': {"description": 'where the reimbursement has been sent',
                              "type": 'string',
                              },
                },
                "type": "dict"
            },
            "type": "list"
        },
        "expense_type": {
            "description": "The type of expense",
            "allowed": ["travel", "business"],
            "required": True,
        },
    },
    "grades": {
        "_description": {
            "description": "The grade for a student on an assignment. This "
                           "information should be private."
        },
        "_id": {
            "description": "unique id, typically the " "student-assignment-course",
            "required": True,
            "type": "string",
        },
        "assignment": {
            "description": "assignment id",
            "required": True,
            "type": "string",
        },
        "course": {"description": "course id", "required": True,
                   "type": "string"},
        "filename": {
            "description": "path to file in store",
            "required": False,
            "type": "string",
        },
        "scores": {
            "description": "the number of points earned on each question",
            "required": True,
            "type": "list",
            "schema": {"anyof_type": ["integer", "float"]},
        },
        "student": {"description": "student id", "required": True,
                    "type": "string"},
    },
    "grants": {
        "_description": {
            "description": "This collection represents grants that have been "
                           "awarded to the group."
        },
        "_id": {
            "description": "short representation, such as this-is-my-name",
            "required": True,
            "type": ("string", "integer", "float"),
        },
        "account": {
            "description": "the account number which holds the funds",
            "required": False,
            "type": "string",
        },
        "admin": {
            "description": "the group administering the grant",
            "type": "string",
            "required": False,
        },
        "alias": {
            "description": "the alias of the grant",
            "type": "string",
            "required": False,
        },
        "amount": {
            "description": "value of award",
            "required": True,
            "type": ("integer", "float"),
        },
        "begin_date": {
            "description": "start date of the grant (if string, in format YYYY-MM-DD)",
            "required": False,
            "anyof_type": ["string", "date"]
        },
        "begin_day": {
            "description": "start day of the grant",
            "required": False,
            "type": "integer",
        },
        "begin_month": {
            "description": "start month of the grant",
            "required": False,
            "anyof_type": ["string", "integer"],
        },
        "begin_year": {
            "description": "start year of the grant",
            "required": False,
            "type": "integer",
        },
        "benefit_of_collaboration": {
            "description": "",
            "required": False,
            "type": "string",
        },
        # TODO: maybe this should move to proposals?
        "call_for_proposals": {"description": "", "required": False,
                               "type": "string"},
        "currency": {
            "description": "typically '$' or 'USD'",
            "required": False,
            "type": "string",
        },
        "end_date": {
            "description": "start date of the grant (if string, in format YYYY-MM-DD)",
            "required": False,
            "anyof_type": ["string", "date"]
        },
        "end_day": {
            "description": "end day of the grant",
            "required": False,
            "type": ("string", "integer"),
        },
        "end_month": {
            "description": "end month of the grant",
            "required": False,
            "anyof_type": ["string", "integer"],
        },
        "end_year": {
            "description": "end year of the grant",
            "required": False,
            "type": "integer",
        },
        "funder": {
            "description": "the agency funding the work",
            "required": True,
            "type": "string",
        },
        "grant_id": {
            "description": "the identifier for this work",
            "required": False,
            "type": "string",
        },
        "institution": {
            "description": "the host institution for the grant",
            "type": "string",
            "required": False,
        },
        "narrative": {"description": "", "required": False, "type": "string"},
        "notes": {
            "description": "notes about the grant",
            "required": False,
            "type": "string",
        },
        "person_months_academic": {
            "description": "Number of months of funding during the academic" "year",
            "required": False,
            "anyof_type": ["integer", "float"],
        },
        "person_months_summer": {
            "description": "Number of months of funding during the summer",
            "required": False,
            "anyof_type": ["integer", "float"],
        },
        "program": {
            "description": "the program the work was funded under",
            "required": True,
            "type": "string",
        },
        # TODO: maybe this should be moved to proposals?
        "status": {
            "allowed": ["pending", "declined", "accepted", "in-prep"],
            "description": "status of the grant",
            "required": False,
            "type": "string",
        },
        "scope": {
            "description": "The scope of the grant, answers the prompt: "
                           '"Describe Research Including Synergies and '
                           'Delineation with Respect to this Proposal/Award:"',
            "required": False,
            "type": "string",
        },
        # TODO: maybe this should be duplicated in proposals?
        "team": {
            "description": "information about the team members participating "
                           "in the grant.",
            "required": True,
            "schema": {
                "schema": {
                    "cv": {"required": False, "type": "string"},
                    "institution": {"required": True, "type": "string"},
                    "name": {"required": True, "type": "string"},
                    "position": {"required": True, "type": "string"},
                    "subaward_amount": {
                        "required": False,
                        "type": ("integer", "float"),
                    },
                },
                "type": "dict",
            },
            "type": "list",
        },
        "title": {
            "description": "actual title of proposal / grant",
            "required": True,
            "type": "string",
        },
        "budget": {
            "description": "budget periods of grant",
            "required": False,
            "schema": {
                "schema": {
                    "begin_date": {
                        "description": "start date of the budget period in format YYYY-MM-DD",
                        "required": False,
                        "anyof_type": ["string", "date"],
                    },
                    "end_date": {
                        "description": "end date of the budget period in format YYYY-MM-DD",
                        "required": False,
                        "anyof_type": ["string", "date"],
                    },
                    "student_months": {
                        "description": "number of months of funding for student members during the academic year",
                        "required": False,
                        "anyof_type": ["float", "integer"]
                    },
                    "postdoc_months": {
                        "description": "number of months of funding for postdoc members during the academic year",
                        "required": False,
                        "anyof_type": ["float", "integer"]
                    },
                    "ss_months": {
                        "description": "number of months of funding for the summer",
                        "required": False,
                        "anyof_type": ["float", "integer"]
                    },
                    "amount": {
                        "description": "subaward for this budget period",
                        "required": False,
                        "anyof_type": ["float", "integer"]
                    }
                },
                "type": "dict",
            },
            "type": "list",
        },
        "proposal_id": {
            "description": "initial proposal made for grant",
            "required": False,
            "type": "string",
        }
    },
    "groups": {
        "_description": {
            "description": "Information about the research group"
                           "this is generally public information"
        },
        "_id": {
            "description": "Unique identifier for submission. This generally "
                           "includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "aka": {
            "required": True,
            "type": "list",
            "description": "other names for the group",
        },
        "banner": {
            "required": False,
            "type": "string",
            "description": "name of image file with the group banner",
        },
        "pi_name": {
            "description": "The name of the Principle Investigator",
            "required": True,
            "type": "string",
        },
        "department": {
            "description": "Name of host department",
            "required": True,
            "type": "string",
        },
        "institution": {
            "description": "Name of the host institution",
            "required": True,
            "type": "string",
        },
        "name": {
            "description": "Name of the group",
            "required": True,
            "type": "string",
        },
        "website": {"description": "URL to group webpage", "type": "string"},
        "mission_statement": {
            "description": "Mission statement of the group",
            "type": "string",
        },
        "projects": {
            "description": "About line for projects",
            "type": "string",
            "required": True,
        },
        "email": {
            "description": "Contact email for the group",
            "type": "string",
            "required": True,
        },
    },
    "institutions": {
        "_description": {
            "description": "This collection will contain all the institutions"
                           "in the world and their departments and addresses"
        },
        "_id": {
            "description": "unique identifier for the institution.",
            "required": True,
            "type": "string",
        },
        "aka": {
            "description": "list of all the different names this "
                           "the institution is known by",
            "required": False,
            "type": "list",
        },
        "city": {
            "description": "the city where the institution is",
            "required": True,
            "type": "string",
        },
        "country": {
            "description": "The country where the institution is",
            "required": True,
            "type": "string",
        },
        "date": {
            "description": "Expense date",
            "required": False,
            "anyof_type": ["string", "date"],
        },
        "day": {
            "description": "the day the entry was created",
            "required": False,
            "type": "integer",
        },
        "departments": {
            "description": "all the departments and centers and"
                           "various units in the institution",
            "required": False,
            "type": "dict",
            # Allow unkown department names, but check their content
            "valuesrules": {
                "type": "dict",
                "schema": {
                    "name": {
                        "description": "The canonical name",
                        "required": True,
                        "type": "string",
                    },
                    "aka": {"required": False, "type": "list"},
                },
            },
        },
        "month": {
            "description": "the month the entry was created",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "name": {
            "description": "the canonical name of the institutions",
            "required": True,
            "type": "string",
        },
        "schools": {
            "description": "this is more for universities, but it "
                           "be used for larger divisions in big "
                           "organizations",
            "required": False,
            "type": "dict",
            "valuesrules": {
                "type": "dict",
                "schema": {
                    "name": {
                        "description": "The canonical name",
                        "required": True,
                        "type": "string",
                    },
                    "aka": {"required": False, "type": "list"},
                },
            },
        },
        "state": {
            "description": "the state where the institution is",
            "required": False,
            "type": "string",
        },
        "street": {
            "description": "the street where the institution is",
            "required": False,
            "type": "string",
        },
        "updated": {
            "description": "a datetime when the entry was updated",
            "required": False,
            "anyof_type": ["string", "datetime", "date"]
        },
        "uuid": {
            "description": "a uuid for the entry",
            "required": False,
            "type": "string",
        },
        "year": {
            "description": "the year the entry was created",
            "required": False,
            "type": "integer",
        },
        "zip": {
            "description": "the zip or postal code of the institution",
            "required": False,
            "anyof_type": ["integer", "string"],
        },
    },
    "meetings": {
        "_id": {
            "description": "unique identifier for the date of the group meeting",
            "required": True,
            "type": "string",
        },
        "actions": {
            "description": "action items expected from the group members for that particular meeting week",
            "required": False,
            "type": "list",
        },
        "agenda": {
            "description": "schedule of the current meeting",
            "required": False,
            "type": "list",
        },
        "buddies": {
            "description": "list of pairs of group members that are selected for the buddy round robin",
            "required": False,
            "type": "list",
        },
        "day": {
            "description": "day of the group meeting",
            "required": False,
            "type": "integer",
        },
        "journal club": {
            "description": "indicating the doi of the journal and the presenting group member as the presenter",
            "required": False,
            "type": "list",
        },
        "lead": {
            "description": "person who will be leading the meeting of the current week",
            "required": False,
            "type":"string",
        },
        "minutes": {
            "description": "meeting notes in a chronological order according to comments made by the group members",
            "required": False,
            "type": "string",
        },
        "month": {
            "description": "month in which the meeting is taking place",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "place": {
            "description": "location where the meeting is taking place on campus",
            "required": False,
            "type": "string",
        },
        "presentation": {
            "description": "indicating the title of the presentation along with the link and the presenter ",
            "required": False,
            "type": "list",
        },
        "scribe": {
            "description": "person who will be taking notes and updating minutes accordingly",
            "required": False,
            "type": "string",
        },
        "time": {
            "description": "person who will be taking notes and updating minutes accordingly",
            "required": False,
            "type": "string",
        },
        "updated": {
            "description": "person who will be taking notes and updating minutes accordingly",
            "required": False,
            "anyof_type": ["string", "datetime", "date"],
        },
        "uuid": {
            "description": "person who will be taking notes and updating minutes accordingly",
            "required": False,
            "type": "string",
        },
        "year": {
            "description": "person who will be taking notes and updating minutes accordingly",
            "required": False,
            "type": "integer",
    },
    "people": {
        "_description": {
            "description": "This collection describes the members of the "
                           "research group.  This is normally public data."
        },
        "_id": {
            "description": "unique identifier for the group member",
            "required": True,
            "type": "string",
        },
        "active": {
            "description": "If the person is an active member, default True.",
            "required": False,
            "type": "boolean",
        },
        "aka": {
            "description": "list of aliases (also-known-as), useful for "
                           "identifying the group member in citations or "
                           "elsewhere.",
            "required": True,
            "type": ["string", "list"],
        },
        "appointments": {
            "type": "dict",
            "required": False,
            "description": "begin and end date, grant loading status and notes about appointments"
        },
        "activities": {
            "type": "list",
            "required": False,
            "description": "activities may be teaching or research things",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "required": False,
                        "description": "the day the activity took place",
                        "type": "integer",
                    },

                    "type": {
                        "required": True,
                        "description": "the type of the acitivity",
                        "type": "string",
                        "eallowed": ["teaching", "research"]
                    },
                    "month": {
                        "required": False,
                        "description": "the month the activity took place",
                        "anyof_type": ["integer", "string"],
                    },
                    "name": {
                        "required": True,
                        "description": "brief statement of the activity",
                        "type": "string",
                    },
                    "other": {
                        "required": False,
                        "description": "longer statement of the activity",
                        "type": "string",
                    },
                    "year": {
                        "required": True,
                        "description": "the year the activity took place",
                        "type": "integer",
                    },
                }
            }
        },
        "avatar": {"description": "URL to avatar", "required": True,
                   "type": "string"},
        "bio": {
            "description": "short biographical text",
            "required": True,
            "type": "string",
        },
        "bios": {
            "description": "longer biographical text if needed",
            "required": False,
            "anyof_type": ["string", "list"]
        },
        "collab": {
            "description": "If the person is a collaborator, default False.",
            "required": False,
            "type": "boolean",
        },
        "committees": {
            "description": "Committees that are served on",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {"required": True, "type": "string",
                             "description": "name of committee, or person if it "
                                            "is a phd committee"},
                    "day": {"required": False, "type": "integer"},
                    "month": {"required": False,
                              "anyof_type": ["string", "integer"],
                              },
                    "notes": {"required": False,
                              "description": "extra things you want to record about the thing",
                              "anyof_type": ["string", "list"],
                              },
                    "year": {"required": True, "type": "integer"},
                    "unit": {"required": False, "type": "string",
                             "description": "name of department or school etc."},
                    "type": {"required": False, "type": "string",
                             "description": "type of committee, department, school, university, external",
                             "eallowed": ["phdoral", "phddefense", "phdproposal", "promotion"]},
                    "level": {
                        "required": True,
                        "type": "string",
                        "description": "department or school or university, or external",
                        "eallowed": ["department", "school", "university", "external"]
                    },
                    "group": {
                        "required": False,
                        "type": "string",
                        "description": "this employment is/was in"
                                       "a group in groups coll",
                    },
                },
            },
            "type": "list",
        },
        "education": {
            "description": "This contains the educational information for "
                           "the group member.",
            "required": True,
            "schema": {
                "type": "dict",
                "schema": {
                    "advisor": {"required": False, "type": "string",
                                "description": "name or id of advisor for this degree"},
                    "begin_day": {"required": False,
                                  "type": "integer"},
                    "begin_month": {"required": False,
                                    "anyof_type": ["string", "integer"],
                                    },
                    "begin_year": {"required": True, "type": "integer"},
                    "degree": {"required": True, "type": "string"},
                    "department": {
                        "required": False,
                        "type": "string",
                        "description": "department within" "the institution",
                    },
                    "group": {
                        "required": False,
                        "type": "string",
                        "description": "this employment is/was in"
                                       "a group in groups coll",
                    },
                    "end_day": {"required": False,
                                "type": "integer"},
                    "end_month": {"required": False,
                                  "anyof_type": ["string", "integer"],
                                  },
                    # Could be ongoing with undefined end
                    "end_year": {"required": False, "type": "integer"},
                    "gpa": {"required": False, "type": ("float", "string")},
                    "institution": {"required": True, "type": "string"},
                    "location": {"required": False, "type": "string"},
                    "other": {"required": False, "type": "list"},
                },
            },
            "type": "list",
        },
        "email": {
            "description": "email address of the group member",
            "required": False,
            "type": "string",
        },
        "employment": {
            "description": "Employment information, similar to educational "
                           "information.",
            "required": False,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "advisor": {"required": False, "type": "string",
                                "description": "name or id of "
                                               "advisor/mentor/manager"},
                    "begin_day": {"required": False, "type": "integer"},
                    "begin_month": {"required": False,
                                    "anyof_type": ["string", "integer"],
                                    },
                    "begin_year": {"required": False, "type": "integer"},
                    "begin_date": {"required": False, "anyof_type": ["string", "date", "datetime"],
                                   "description": "begin date of employment in format YYYY-MM-DD"},
                    "coworkers": {"required": False, "type": "list",
                                  "description": "list of coworkers.  If"
                                                 "position is editor, these are "
                                                 "assumed to be coeditors in"
                                                 "conflict of interest builder"},
                    "department": {"required": False, "type": "string"},
                    "end_day": {"required": False, "type": "integer"},
                    "end_month": {"required": False,
                                  },
                    "end_year": {"required": False, "type": "integer"},
                    "end_date": {"required": False, "anyof_type": ["string", "date", "datetime"],
                                 "description": "end date of employment in format YYYY-MM-DD"},
                    "group": {
                        "required": False,
                        "type": "string",
                        "description": "this employment is/was in"
                                       "a group in groups coll",
                    },
                    "location": {"required": False, "type": "string"},
                    "organization": {"required": True, "type": "string"},
                    "other": {"required": False, "type": "list"},
                    "permanent": {"required": False, "type": "boolean",
                                  "description": "true if the position is open " \
                                                 "ended and has no fixed end-date"},
                    "position": {"required": True, "type": "string",
                                 "eallowed": list(SORTED_POSITION)},
                    "position_full": {
                        "description": "The full on title of the position.  This will be "
                                       "typeset if it is here, or if not Position will be "
                                       "used.  Position will be used for sorting and must "
                                       "come from a fixed list of positions",
                        "required": False,
                        "type": "string",
                    },
                    "status": {"required": False, "type": "string", "eallowed": [
                        "pi",
                        "adjunct",
                        "high-school",
                        "undergrad",
                        "ms",
                        "phd",
                        "postdoc",
                        "visitor-supported",
                        "visitor-unsupported"],
                               },
                },
            },
        },
        "facilities": {
            "type": "list",
            "required": False,
            "description": "facilities may be teaching or research things",
            "schema": {
                "type": "dict",
                "schema": {
                    "begin_day": {
                        "required": False,
                        "description": "the day facility, or the wish for the "
                                       "facility, started",
                        "type": "integer",
                    },
                    "end_day": {
                        "required": False,
                        "description": "the day facility started",
                        "type": "integer",
                    },
                    "type": {
                        "required": True,
                        "description": "the type of the facility. Columbia asks"
                                       "for wished-for facilities, so there are "
                                       "teaching-wish and research-wish fields.",
                        "type": "string",
                        "eallowed": ["teaching", "research", "shared", "other", "teaching_wish",
                                     "research_wish"]
                    },
                    "begin_month": {
                        "required": False,
                        "description": "the month the facility (or wish) started",
                        "anyof_type": ["integer", "string"],
                    },
                    "end_month": {
                        "required": False,
                        "description": "the month the faclity went away",
                        "anyof_type": ["integer", "string"],
                    },
                    "name": {
                        "required": True,
                        "description": "description of the facility",
                        "type": "string",
                    },
                    "notes": {
                        "required": False,
                        "description": "anything else you want to jot down",
                        "anyof_type": ["string", "list"]
                    },
                    "begin_year": {
                        "required": True,
                        "description": "the year the facility (or wish) started",
                        "type": "integer",
                    },
                    "end_year": {
                        "required": False,
                        "description": "the year the facility (or wish) went away",
                        "type": "integer",
                    },
                }
            }
        },
        "funding": {
            "description": "Funding and scholarship that the group member "
                           "has individually obtained in the past. "
                           "**WARNING:** this is not to be confused with the "
                           "**grants** collection",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "currency": {"required": False, "type": "string"},
                    "duration": {"required": False, "type": "string"},
                    "month": {"required": False,
                              "anyof_type": ["string", "integer"],
                              },
                    "name": {"required": True, "type": "string"},
                    "value": {"required": True, "type": ("float", "integer")},
                    "year": {"required": True, "type": "integer"},
                },
            },
            "type": "list",
        },
        "github_id": {"required": False, "type": "string",
                      "description": "Your GitHub ID"},
        "google_scholar_url": {"required": False, "type": "string",
                               "description": "URL of your Google Scholar "
                                              "rofile"},
        "hindex": {
            "description": "details of hindex pulled on a certain date",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "h": {"description": "the value of the h index",
                          "required": True, "type": "integer"},
                    "h_last_five": {"description": "h index over past 5 years",
                                    "required": False, "type": "integer"},
                    "citations": {"description": "total number of citations",
                                  "required": False, "type": "integer"},
                    "citations_last_five": {"description": "number of citations"
                                                           "in the past 5 years",
                                            "required": False, "type": "integer"},
                    "origin": {"description": "where the numbers came from",
                               "required": False, "type": "string"},
                    "since": {"description": "year of first citation",
                              "required": False, "type": "integer"},
                    "year": {"description": "year when the data were pulled",
                             "required": False, "type": "integer"},
                    "month": {"description": "month when the data were pulled",
                              "required": False, "anyof_type": ["string", "integer"]},
                    "day": {"description": "day when the data were pulled",
                            "required": False, "type": "integer"},
                }
            },
            "type": "list",
        },
        "home_address": {
            "description": "The person's home address",
            "type": "dict",
            "schema": {
                "street": {"type": "string", "description": "street address"},
                "city": {"type": "string", "description": "name of home city"},
                "state": {"type": "string", "description": "name o home state"},
                "zip": {"type": "string", "description": "zip code"},
            },
        },
        "honors": {
            "description": "Honors that have been awarded to this " "group member",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "description": {"required": False, "type": "string"},
                    "month": {"required": False,
                              "anyof_type": ["string", "integer"],
                              },
                    "name": {"required": True, "type": "string"},
                    "year": {"required": True, "type": "integer"},
                },
            },
            "type": "list",
        },
        "initials": {
            "description": "The canonical initials for this group member",
            "required": False,
            "type": "string",
        },
        # TODO: include `link`
        "membership": {
            "description": "Professional organizations this member is " "a part of",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "begin_month": {"required": False,
                                    "anyof_type": ["string", "integer"],
                                    },
                    "begin_year": {"required": True, "type": "integer"},
                    "description": {"required": False, "type": "string"},
                    "end_month": {"required": False,
                                  "anyof_type": ["string", "integer"],
                                  },
                    "end_year": {"required": False, "type": "integer"},
                    "organization": {"required": True, "type": "string"},
                    "position": {"required": True, "type": "string"},
                    "website": {"required": False, "type": "string"},
                },
            },
            "type": "list",
        },
        "miscellaneous": {
            "description": "Place to put weird things needed for special reporta",
            "required": False,
            "type": "dict",
            "schema": {
                "metrics_for_success": {
                    "description": "How do I want to be judged",
                    "required": False,
                    "type": "list",
                },
            },
        },
        "name": {
            "description": "Full, canonical name for the person",
            "required": True,
            "type": "string",
        },
        "office": {
            "description": "The person's office",
            "type": "string",
            "required": False
        },
        "orcid_id": {
            "description": "The ORCID ID of the person",
            "required": False,
            "type": "string",
        },
        "position": {
            "description": "such as professor, graduate student, or scientist",
            "required": False,
            "type": "string",
            "eallowed": list(SORTED_POSITION),
        },
        "position_full": {
            "description": "The full on title of the position.  This will be "
                           "typeset if it is here, or if not Position will be "
                           "used.  Position will be used for sorting and must "
                           "come from a fixed list of positions",
            "required": False,
            "type": "string",
        },
        "publicity": {
            "description": "summary of publicity that person has received",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "type": {"required": True, "type": "string",
                             "eallowed": ["online", "article"]},
                    "topic": {"required": False, "type": "string",
                              "description": "The short sentence of what the "
                                             "publicity was about",
                              },
                    "title": {"required": True, "type": "string",
                              "description": "The title of the piece",
                              },
                    "day": {"required": False, "type": "integer",
                            "description": "The day the piece appeared"
                            },
                    "month": {"required": False, "anyof_type": ["string",
                                                                "integer"],
                              "description": "The month the piece appeared"
                              },
                    "publication": {"required": False, "type": "string",
                                    "description": "The place where the "
                                                   "publicity was placed"
                                    },
                    "text": {"required": False, "type": "string",
                             "description": "The text of the publicity",
                             },
                    "url": {"required": False, "type": "string",
                            "description": "The URL where the piece may be found"
                            },
                    "year": {"required": True, "type": "integer",
                             "description": "The year the piece appeared"
                             },
                    "grant": {"required": True, "type": "string",
                              "description": "The identifier of the grant "
                                             "associated with the piece"
                              },
                },
            },
            "type": "list"
        },
        "research_focus_areas": {
            "description": "summary of research projects that are ongoing. Used"
                           "in Annual appraisal for example",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "begin_year": {"required": False, "type": "integer"},
                    "end_year": {"required": False, "type": "integer"},
                    "description": {"required": False, "type": "string"}
                },
            },
            "type": "list"
        },
        "research_summary": {
            "description": "Brief summary of overarching research goals",
            "required": False,
            "type": "string",
        },
        "service": {
            "description": "Service that this group member has provided",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "description": {"required": False, "type": "string"},
                    "duration": {"required": False, "type": "string"},
                    "month": {"description": "Use month and year if the service"
                                             "doesn't extend more than one year."
                                             "Otherwise use begin_year and end_year",
                              "required": False,
                              "anyof_type": ["string", "integer"]
                              },
                    "name": {"required": True, "type": "string"},
                    "role": {"required": False, "type": "string",
                             "description": "the role played in the activity, e.g., co-chair"},
                    "notes": {"required": False, "anyof_type": ["string", "list"]},
                    "year": {"required": False, "type": "integer"},
                    "begin_year": {"required": False, "type": "integer"},
                    "begin_day": {"required": False, "type": "integer"},
                    "begin_month": {"description": "Use month and year if the service"
                                                   "doesn't extend more than one year."
                                                   "Otherwise use begin_year/month and end_year/month",
                                    "required": False,
                                    "anyof_type": ["string", "integer"]
                                    },
                    "end_year": {"required": False, "type": "integer"},
                    "end_month": {"description": "Use month and year if the service"
                                                 "doesn't extend more than one year."
                                                 "Otherwise use begin_year and end_year",
                                  "required": False,
                                  "anyof_type": ["string", "integer"]
                                  },
                    "end_day": {"required": False, "type": "integer"},
                    "other": {"required": False,
                              "anyof_type": ["string", "list"]},
                    "type": {"required": True, "type": "string",
                             "description": "profession, department, school, university",
                             "eallowed": ["profession", "university",
                                          "school", "department"]},
                },
            },
            "type": "list",
        },
        "skills": {
            "description": "Skill the group member has",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "category": {"required": True, "type": "string"},
                    "level": {"required": True, "type": "string"},
                    "name": {"required": True, "type": "string"},
                },
            },
            "type": "list",
        },
        "teaching": {
            "description": "Courses that this group member has taught, if any",
            "required": False,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "course": {"required": True, "type": "string"},
                    "courseid": {"required": True, "type": "string"},
                    "description": {"required": False, "type": "string"},
                    "end_month": {"required": False,
                                  "anyof_type": ["string", "integer"]},
                    "end_year": {"required": False, "type": "integer"},
                    "enrollment": {"required": False, "anyof_type": ["integer", "string"]},
                    "evaluation": {
                        "type": "dict",
                        "required": False,
                        "schema": {
                            "response_rate": {"type": "number", "required": True},
                            "amount_learned": {"type": "number", "required": True},
                            "appropriateness_workload": {"type": "number", "required": True},
                            "course_overall": {"type": "number", "required": True},
                            "fairness_grading": {"type": "number", "required": True},
                            "organization": {"type": "number", "required": True},
                            "classroom_delivery": {"type": "number", "required": True},
                            "approachability": {"type": "number", "required": True},
                            "instructor_overall": {"type": "number", "required": True},
                            "comments": {"type": "list", "required": False,
                                         "description": "student comments"},
                        },
                    },
                    "materials": {"required": False, "type": "string"},
                    "month": {"required": False,
                              "anyof_type": ["string", "integer"],
                              },
                    "organization": {"required": True, "type": "string"},
                    "position": {"required": True, "type": "string"},
                    "semester": {"required": False, "type": "string"},
                    "syllabus": {"required": False, "type": "string"},
                    "video": {"required": False, "type": "string"},
                    "website": {"required": False, "type": "string"},
                    "year": {"required": True, "type": "integer"},
                },
            },
        },
        "title": {
            "description": "for example, Dr., etc.",
            "required": False,
            "type": "string",
        },
        "todos": {
            "description": "a list of the todo tasks",
            "required": False,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "description": {"description": "the description of the to-do task",
                                    "required": True,
                                    "type": "string"},
                    "due_date": {"description": "the due date",
                                 "required": False,
                                 "anyof_type": ["string", "date"]},
                    "begin_date": {"description": "the begin date",
                                   "required": False,
                                   "anyof_type": ["string", "date"]},
                    "end_date": {"description": "the end date",
                                 "required": False,
                                 "anyof_type": ["string", "date"]},
                    "duration": {
                        "description": "the size of the task/ the estimated duration it will take to finish the task. Unit: miniutes.",
                        "required": False,
                        "type": "float"},
                    "importance": {
                        "description": "the importance, from 0 to 2",
                        "required": False,
                        "type": "integer"},
                    "status": {"description": "the status: started/finished/cancelled",
                               "required": True,
                               "type": "string"},
                    "notes": {"description": "additional notes for this task",
                              "required": False,
                              "type": "list",
                              "schema": {"type": "string"}
                              },
                    "running_index": {
                        "description": "Index of a certain task used to update that task in the enumerated todo list.",
                        "required": False,
                        "type": "integer"},
                    "assigned_by": {
                        "description": "ID of the member that assigns the task",
                        "required": False,
                        "type": "string"},

                }
            }
        },
    },
    "presentations": {
        "_description": {
            "description": "This collection describes presentations that group"
                           "members make at conferences, symposia, seminars and"
                           "so on."
        },
        "_id": {
            "description": "unique id for the presentation",
            "required": True,
            "type": "string",
        },
        "abstract": {
            "description": "abstract of the presentation",
            "required": False,
            "type": "string",
        },
        "authors": {
            "description": "Author list.",
            "required": True,
            "anyof_type": ["string", "list"],
        },
        "begin_date": {
            "description": "begin date in YYYY-MM-DD",
            "anyof_type": ["date", "string"],
        },
        "end_date": {
            "description": "end_date in YYYY-MM-DD",
            "anyof_type": ["date", "string"],
        },
        "begin_year": {
            "description": "year the conference or trip begins.",
            "required": False,
            "type": "integer",
        },
        "begin_month": {"required": False,
                        "anyof_type": ["string", "integer"],
                        },
        "begin_day": {"required": False, "type": "integer"},
        "department": {
            "description": "department of the institution where the"
                           "presentation will be made, if "
                           "applicable.  should be discoverable in "
                           "institutions.",
            "required": False,
            "type": "string",
        },
        "end_year": {
            "description": "year the conference or trip ends",
            "required": False,
            "type": "integer",
        },
        "end_month": {"required": False,
                      "anyof_type": ["string", "integer"],
                      },
        "end_day": {"required": False, "type": "integer"},
        "institution": {
            "description": "institution where the"
                           "presentation will be made, if "
                           "applicable.",
            "required": False,
            "type": "string",
        },
        "meeting_name": {
            "description": "full name of the conference or "
                           "meeting.  If it is a departmental "
                           "seminar or colloquium, write Seminar"
                           "or Colloquium and fill in department "
                           "and institution fields",
            "required": False,
            "type": "string",
        },
        # TODO: conditional validation.  If type=colloq or seminar, required is
        # institution and department, otherwise location
        "location": {
            "description": "city and {state or country} of meeting",
            "required": False,
            "type": "string",
        },
        "notes": {
            "description": "any reminder or memory aid about anything",
            "required": False,
            "anyof_type": ["list", "string"],
        },
        "project": {
            "description": "project or list of projects that this "
                           "presentation is associated with.  Should "
                           "be discoverable in projects collection",
            "required": False,
            "anyof_type": ["string", "list"],
        },
        "status": {
            "description": "Is the application in prep or submitted, "
                           "was the invitation accepted or declined, was "
                           "the trip cancelled?",
            "required": True,
            "type": "string",
            "eallowed": ["in-prep", "submitted", "accepted", "declined",
                         "cancelled"],
        },
        "title": {
            "description": "title of the presentation",
            "required": True,
            "type": "string",
        },
        "type": {
            "description": "type of presentation",
            "eallowed": PRESENTATIONS_TYPE,
            "required": True,
            "type": "string",
        },
        "webinar": {
            "description": "true if a webinar. Default to False",
            "required": False,
            "type": "boolean",
        },
    },
    "projects": {
        "_description": {
            "description": "This collection describes the research group "
                           "projects. This is normally public data."
        },
        "_id": {
            "description": "Unique project identifier.",
            "required": True,
            "type": "string",
        },
        "active": {
            "description": "true if the project is active",
            "required": False,
            "anyof_type": ["string", "boolean"],
        },
        "description": {
            "description": "brief project description.",
            "required": True,
            "type": "string",
        },
        "grant": {
            "description": "Grant id if there is a grant supporting this " "project",
            "required": False,
            "type": "string",
        },
        "group": {
            "description": "id for the group in the groups collection whose project this is",
            "required": False,
            "type": "string",
        },
        "highlights": {
            "description": "list of things to highlight in a report or website, such as releases for  for software or high profile publications",
            "required": False,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "year": {"description": "the year of the highlight",
                             "required": True,
                             "type": "integer"},
                    "month": {"description": "the month of the highlight",
                              "required": True,
                              "anyof_type": ["string", "integer"]},
                    "description": {"description": "the highlight",
                                    "required": True,
                                    "type": "string"},
                }
            }
        },
        "logo": {
            "description": "URL to the project logo",
            "required": False,
            "type": "string",
        },
        "name": {
            "description": "name of the project.",
            "required": True,
            "type": "string",
        },
        "other": {
            "description": "other information about the project",
            "required": False,
            "type": ["list", "string"],
        },
        "repo": {
            "description": "URL of the source code repo, if available",
            "required": False,
            "type": "string",
        },
        "team": {
            "description": "People who are/have been working on this project.",
            "required": True,
            "schema": {
                "type": "dict",
                "schema": {
                    "begin_month": {"required": False,
                                    "anyof_type": ["string", "integer"],
                                    },
                    "begin_year": {"required": True, "type": "integer"},
                    "end_month": {"required": False,
                                  "anyof_type": ["string", "integer"],
                                  },
                    "end_year": {"required": False, "type": "integer"},
                    "name": {"required": True, "type": "string"},
                    "position": {"required": True, "type": "string"},
                },
            },
            "type": "list",
        },
        "type": {
            "description": "The type of project",
            "required": False,
            "anyof_type": ["string"],
            "eallowed": ["ossoftware", "funded"]
        },
        "website": {
            "description": "URL of the website.",
            "required": False,
            "type": "string",
        },
    },
    "proposalReviews": {
        "_description": {
            "description": "This collection contains reviews of funding proposals"
        },
        "_id": {
            "description": "ID, e.g. 1906_doe_example",
            "required": True,
            "type": ("string", "integer", "float"),
        },
        "adequacy_of_resources": {
            "description": "Are the resources of the PI adequate",
            "required": True,
            "type": "list",
        },
        "agency": {
            "description": "currently nsf or doe",
            "type": "string",
            "eallowed": ["nsf", "doe"],
        },
        "competency_of_team": {
            "description": "Is the team competent",
            "required": True,
            "type": "list",
        },
        "doe_appropriateness_of_approach": {
            "description": "Appropriateness of Research. only used if agency is doe.",
            "required": False,
            "type": "list",
        },
        "doe_reasonableness_of_budget": {
            "description": "Reasonableness of budget. only used if agency is doe.",
            "required": False,
            "type": "list",
        },
        "doe_relevance_to_program_mission": {
            "description": "Relevance to program mission. only used if agency is doe.",
            "required": False,
            "type": "list",
        },
        "does_how": {
            "description": "How will the research be done",
            "required": True,
            "type": "list",
        },
        "does_what": {
            "description": "What will the team do",
            "required": True,
            "type": "string",
        },
        "due_date": {
            "description": "date the review is due in ISO format",
            "required": True,
            "anyof_type": ["string", "date"],
        },
        "freewrite": {
            "description": "Anything and this will appear in the built document"
                           "right before the summary.  This section often used "
                           "for extra review criteria for the particular proposal",
            "required": False,
            "type": "list",
        },
        "goals": {
            "description": "What are the main goals of the proposed research",
            "required": True,
            "type": "list",
        },
        "importance": {
            "description": "The importance of the Research",
            "required": True,
            "type": "list",
        },
        "institutions": {
            "description": "The institutions of the authors in the same order",
            "required": True,
            "anyof_type": ["string", "list"]
        },
        "month": {
            "description": "The month the review was submitted",
            "required": True,
            "anyof_type": ["string", "integer"],
        },
        "names": {
            "description": "The names of the PIs",
            "required": True,
            "anyof_type": ["list", "string"],
        },
        "nsf_broader_impacts": {
            "description": "The broader impacts of the research.  Only used if "
                           "agency is nsf",
            "required": False,
            "type": "list",
        },
        "nsf_create_original_transformative": {
            "description": "Answer to the question how the work is creative, "
                           "original or transformative.  Only used if agency is "
                           "nsf",
            "required": False,
            "type": "list",
        },
        "nsf_plan_good": {
            "description": "Is the plan good? Only used if agency is nsf",
            "required": False,
            "type": "list",
        },
        "nsf_pot_to_advance_knowledge": {
            "description": "Answer to the question how the work will advance"
                           "knowledge.  Only used if agency is nsf",
            "required": False,
            "type": "list",
        },
        "nsf_pot_to_benefit_society": {
            "description": "Answer to the question how the work has the potential"
                           "to benefit society.  Only used if agency is nsf",
            "required": False,
            "type": "list",
        },
        "requester": {
            "description": "Name of the program officer who requested the review",
            "required": True,
            "type": "string",
        },
        "reviewer": {
            "description": "short name of the reviewer.  Will be used in the "
                           "filename of the resulting text file",
            "required": True,
            "type": "string",
        },
        "status": {
            "description": "the status of the review",
            "type": "string",
            "eallowed": [
                "invited",
                "accepted",
                "declined",
                "downloaded",
                "inprogress",
                "submitted",
                "cancelled"
            ],
        },
        "summary": {
            "description": "Summary statement",
            "required": True,
            "type": "string",
        },
        "title": {
            "description": "The title of the proposal",
            "required": True,
            "type": "string",
        },
        "year": {
            "description": "The year the review was submitted",
            "required": True,
            "type": "integer",
        },
    },
    "proposals": {
        "_description": {
            "description": "This collection represents proposals that have "
                           "been submitted by the group."
        },
        "_id": {
            "description": "short representation, such as this-is-my-name",
            "required": True,
            "type": ("string", "integer", "float"),
        },
        "amount": {
            "description": "value of award",
            "required": True,
            "type": ("integer", "float"),
        },
        "authors": {
            "description": "other investigator names",
            "required": False,
            "anyof_type": ["list", "string"],
        },
        "begin_date": {
            "description": "start date of the proposed grant in format YYYY-MM-DD",
            "required": False,
            "anyof_type": ["string", "date"]
        },
        "begin_day": {
            "description": "start day of the proposed grant",
            "required": False,
            "type": "integer",
        },
        "begin_month": {
            "description": "start month of the proposed grant",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "begin_year": {
            "description": "start year of the proposed grant",
            "required": False,
            "type": "integer",
        },
        "call_for_proposals": {
            "description": "",
            "required": False,
            "type": "string",
        },
        "cpp_info": {
            "description": "extra information needed for building current and "
                           "pending form ",
            "required": False,
            "schema": {
                "cppflag": {"required": False, "type": "boolean"},
                "other_agencies_submitted": {"required": False,
                                             "anyof_type": ["string", "boolean"]},
                "institution": {"required": False, "type": "string",
                                "description": "place where the proposed grant will be located"},
                "person_months_academic": {"required": False,
                                           "anyof_type": ["float", "integer"]},
                "person_months_summer": {"required": False,
                                         "anyof_type": ["float", "integer"]},
                "project_scope": {"required": False, "type": "string"},
            },
            "type": "dict",
        },
        "currency": {
            "description": "typically '$' or 'USD'",
            "required": True,
            "type": "string",
        },
        "day": {
            "description": "day that the proposal was submitted",
            "required": False,
            "type": "integer",
        },
        "due_date": {
            "description": "day that the proposal is due",
            "required": False,
            "anyof_type": ["string", "date"],
        },
        "duration": {
            "description": "number of years",
            "required": False,
            "type": ("integer", "float"),
        },
        "end_date": {
            "description": "end date of the proposed grant in format YYYY-MM-DD",
            "required": False,
            "anyof_type": ["string", "date"]
        },
        "end_day": {
            "description": "end day of the proposed grant",
            "required": False,
            "type": ("string", "integer"),
        },
        "end_month": {
            "description": "end month of the proposed grant",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "end_year": {
            "description": "end year of the proposed grant",
            "required": False,
            "type": "integer",
        },
        "funder": {
            "description": "who will fund the proposal"
                           "as funder in grants",
            "required": False,
            "type": "string",
        },
        "full": {
            "description": "full body of the proposal",
            "required": False,
            "type": "dict",
        },
        "month": {
            "description": "month that the proposal was submitted",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "notes": {
            "description": "anything you want to note",
            "required": False,
            "anyof_type": ["string", "list"],
        },
        "pi": {
            "description": "principal investigator name",
            "required": True,
            "type": "string",
        },
        "pre": {
            "description": "Information about the pre-proposal",
            "required": False,
            "type": "dict",
        },
        "status": {
            "description": "e.g. 'pending', 'accepted', 'rejected'",
            "required": True,
            "type": "string",
            "eallowed": ["pending", "declined", "accepted", "inprep",
                         "submitted"],
        },
        "team": {
            "description": "information about the team members participating "
                           "in the grant.",
            "required": False,
            "schema": {
                "schema": {
                    "cv": {"required": False, "type": "string"},
                    "email": {"required": False, "type": "string"},
                    "institution": {"required": False, "type": "string"},
                    "name": {"required": False, "type": "string"},
                    "position": {"required": False, "type": "string"},
                    "subaward_amount": {
                        "required": False,
                        "type": ("integer", "float"),
                    },
                },
                "type": "dict",
            },
            "type": "list",
        },
        "title": {
            "description": "actual title of proposal",
            "required": True,
            "type": "string",
        },
        "title_short": {
            "description": "short title of proposal",
            "required": False,
            "type": "string",
        },
        "year": {
            "description": "Year that the proposal was submitted",
            "required": False,
            "type": "integer",
        },
    },
    "refereeReports": {
        "_description": {
            "description": "This is a collection of information that will be "
                           "be used to build a referee report. This should probably be private."
        },
        "_id": {"description": "the ID", "required": True, "type": "string"},
        "claimed_found_what": {
            "description": "What the authors claim to have found",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "claimed_why_important": {
            "description": "What importance the authors claim",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "did_how": {
            "description": "How the study was done",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "did_what": {
            "description": "What the study was",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "due_date": {
            "description": "date the review is due in ISO format",
            "required": True,
            "anyof_type": ["string", "date"],
        },
        "editor_eyes_only": {
            "description": "Comments you don't want passed to the author",
            "required": False,
            "type": "string",
        },
        "final_assessment": {
            "description": "Summary of impressions of the study",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "first_author_last_name": {
            "description": "Last name of first author will be referred to "
                           "with et al.",
            "required": True,
            "type": "string",
        },
        "freewrite": {
            "description": "Things that you want to add that don't fit into "
                           "any category above",
            "required": False,
            "type": "string",
        },
        "journal": {
            "description": "name of the journal",
            "required": True,
            "type": "string",
        },
        "month": {
            "description": "the month the entry was created",
            "required": False,
            "anyof_type": ["string", "integer"]
        },
        "recommendation": {
            "description": "Your publication recommendation",
            "required": True,
            "type": "string",
            "eallowed": ["reject", "asis", "smalledits", "diffjournal",
                         "majoredits"],
        },
        "requester": {
            "description": "Name of the program officer who requested the review",
            "required": True,
            "type": "string",
        },
        "reviewer": {
            "description": "name of person reviewing the paper",
            "required": True,
            "type": "string",
        },
        "status": {
            "description": "Where you are with the review",
            "required": True,
            "type": "string",
            "eallowed": [
                "invited",
                "accepted",
                "declined",
                "downloaded",
                "inprogress",
                "submitted",
                "cancelled"
            ],
        },
        "submitted_date": {
            "description": "submitted date in ISO YYYY-MM-DD format",
            "required": True,
            "anyof_type": ["string", "date"],
        },
        "title": {
            "description": "title of the paper under review",
            "required": True,
            "type": "string",
        },
        "validity_assessment": {
            "description": "List of impressions of the validity of the claims",
            "required": True,
            "schema": {"type": "string", "required": True},
            "type": "list",
        },
        "year": {
            "description": "year when the review is being done",
            "required": True,
            "anyof_type": ["string", "integer"],
        },
    },
    "students": {
        "_description": {
            "description": "This is a collection of student names and "
                           "metadata. This should probably be private."
        },
        "_id": {
            "description": "short representation, such as this-is-my-name",
            "required": True,
            "type": "string",
        },
        "aka": {
            "description": "list of aliases",
            "required": False,
            "schema": {"type": "string"},
            "type": ("list", "string"),
        },
        "email": {"description": "email address", "required": False,
                  "type": "string"},
        "university_id": {
            "description": "The university identifier for the student",
            "required": False,
            "type": "string",
        },
    },
},
}

for s in SCHEMAS:
    SCHEMAS[s]["files"] = {
        "description": "Files associated with the document",
        # TODO: fix this since this is currently comming out a CommentedMap
        # "type": "list",
        # "schema": {"type": "string"},
        "required": False,
    }


class NoDescriptionValidator(Validator):
    def _validate_description(self, description, field, value):
        """Don't validate descriptions

        The rule's arguments are validated against this schema:
        {'type': 'string'}"""
        if False:
            pass

    def _validate_eallowed(self, eallowed, field, value):
        """Test if value is in list
        The rule's arguments are validated against this schema:
        {'type': 'list'}
        """
        if value not in eallowed:
            warn(
                '"{}" is not in the preferred entries for "{}", please '
                "consider changing this entry to conform or add this to the "
                "``eallowed`` field in the schema.".format(value, field)
            )


def validate(coll, record, schemas):
    """Validate a record for a given db

    Parameters
    ----------
    coll : str
        The name of the db in question
    record : dict
        The record to be validated
    schemas : dict
        The schema to validate against

    Returns
    -------
    rtn : bool
        True is valid
    errors: dict
        The errors encountered (if any)

    """
    if coll in schemas:
        schema = copy.deepcopy(schemas[coll])
        v = NoDescriptionValidator(schema)
        return v.validate(record), v.errors
    else:
        return True, ()

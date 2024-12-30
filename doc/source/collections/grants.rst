Grants
======
This collection represents grants that have been awarded to the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ['string', 'integer', 'float'], short representation, such as this-is-my-name, required
:account: string, the account number which holds the funds, optional
:admin: string, the unit or group administering the grant, optional
:alias: string, the alias of the grant, optional
:amount: ['integer', 'float'], value of award, required
:awardnr: string, the number of the award from the agency, optional
:begin_date: ['string', 'date'], start date of the grant (if string, in format YYYY-MM-DD), optional
:begin_day: integer, start day of the grant, optional
:begin_month: ['string', 'integer'], start month of the grant, optional
:begin_year: integer, start year of the grant, optional
:benefit_of_collaboration: string, optional
:budget: list, budget periods of grant, optional

	:type: dict, optional

		:begin_date: ['string', 'date'], start date of the budget period in format YYYY-MM-DD, optional
		:end_date: ['string', 'date'], end date of the budget period in format YYYY-MM-DD, optional
		:student_months: ['float', 'integer'], number of months of funding for student members during the academic year, optional
		:postdoc_months: ['float', 'integer'], number of months of funding for postdoc members during the academic year, optional
		:ss_months: ['float', 'integer'], number of months of funding for the summer, optional
		:amount: ['float', 'integer'], subaward for this budget period, optional
:call_for_proposals: string, optional
:currency: string, typically '$' or 'USD', optional
:end_date: ['string', 'date'], start date of the grant (if string, in format YYYY-MM-DD), optional
:end_day: ['string', 'integer'], end day of the grant, optional
:end_month: ['string', 'integer'], end month of the grant, optional
:end_year: integer, end year of the grant, optional
:funder: string, the agency funding the work, required
:funds_available: list, funds available on date, optional

	:type: dict, optional

		:date: ['string', 'date'], optional
		:funds_available: ['integer', 'float'], optional
:grant_id: string, the identifier for this work, optional
:highlights: list, lists of highlights from the project, optional

	:type: dict, optional

		:year: integer, optional
		:month: integer, optional
		:description: string, optional
:institution: string, the host institution for the grant, optional
:narrative: string, optional
:notes: string, notes about the grant, optional
:person_months_academic: ['integer', 'float'], Number of months of funding during the academic year, optional
:person_months_summer: ['integer', 'float'], Number of months of funding during the summer, optional
:program: string, the program the work was funded under, optional
:proposal_id: string, initial proposal made for grant, optional
:scope: string, The scope of the grant, answers the prompt: Describe Research Including Synergies and Delineation with Respect to this Proposal/Award:, optional
:status: string, status of the grant, optional

	Allowed values:
		* pending
		* declined
		* accepted
		* in-prep
:team: list, information about the team members participating in the grant., required

	:type: dict, optional

		:admin_people: list, optional
		:cv: string, optional
		:institution: string, optional
		:name: string, optional
		:position: string, optional

			Allowed values:
				* pi
				* copi
		:subaward_amount: ['integer', 'float'], optional
:title: string, actual title of proposal / grant, required


YAML Example
------------

.. code-block:: yaml

	SymPy-1.1:
	  admin: APAM
	  alias: sym
	  amount: 3000.0
	  awardnr: NF-1234
	  begin_day: 1
	  begin_month: May
	  begin_year: 2030
	  budget:
	    - amount: 1000.0
	      begin_date: '2030-05-01'
	      end_date: '2030-06-30'
	      postdoc_months: 0.0
	      ss_months: 1.0
	      student_months: 0.5
	    - amount: 1000.0
	      begin_date: '2030-07-01'
	      end_date: '2030-09-30'
	      postdoc_months: 0.0
	      ss_months: 2.0
	      student_months: 1.5
	    - amount: 1000.0
	      begin_date: '2030-10-01'
	      end_date: '2030-12-31'
	      postdoc_months: 0.0
	      ss_months: 0.0
	      student_months: 3.0
	  call_for_proposals: https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ
	  end_day: 31
	  end_month: December
	  end_year: 2030
	  funder: NumFOCUS
	  funds_available:
	    - date: '2020-04-01'
	      funds_available: 2800.0
	    - date: '2021-01-03'
	      funds_available: 2100.0
	    - date: '2020-07-21'
	      funds_available: 2600.0
	  narrative: https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing
	  program: Small Development Grants
	  team:
	    - institution: University of South Carolina
	      name: Anthony Scopatz
	      position: pi
	    - admin_people:
	        - A. D. Ministrator
	      institution: University of South Carolina
	      name: Aaron Meurer
	      position: researcher
	  title: SymPy 1.1 Release Support
	SymPy-2.0:
	  admin: APAM
	  alias: sym2.0
	  amount: 3000.0
	  awardnr: NF-1234
	  begin_day: 1
	  begin_month: 6
	  begin_year: 2019
	  call_for_proposals: https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ
	  end_day: 31
	  end_month: December
	  end_year: 2030
	  funder: NumFOCUS
	  funds_available:
	    - date: '2020-04-01'
	      funds_available: 2800.0
	    - date: '2021-01-03'
	      funds_available: 2100.0
	    - date: '2020-07-21'
	      funds_available: 2600.0
	  highlights:
	    - description: high profile pub in Nature
	      month: 5
	      year: 2020
	  narrative: https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing
	  program: Small Development Grants
	  proposal_id: SymPy-2.0
	  status: accepted
	  team:
	    - institution: University of South Carolina
	      name: Anthony Scopatz
	      position: pi
	    - institution: University of South Carolina
	      name: Aaron Meurer
	      position: researcher
	  title: SymPy 2.0 Release Support
	abc42:
	  alias: abc42
	  amount: 42000.0
	  begin_date: '2020-06-01'
	  budget:
	    - amount: 42000.0
	      begin_date: '2020-06-01'
	      end_date: '2020-12-31'
	      postdoc_months: 0.0
	      ss_months: 1.0
	      student_months: 0.0
	  end_date: '2020-12-31'
	  funder: Life
	  program: Metaphysical Grants
	  proposal_id: abc42
	  team:
	    - institution: University of Pedagogy
	      name: Chief Pedagogue
	      position: pi
	    - institution: University of Pedagogy
	      name: Pedagogue Jr.
	      position: copi
	  title: The answer to life, the universe, and everything
	dmref15:
	  account: GG012345
	  admin: DSI
	  alias: dmref15
	  amount: 982785.0
	  awardnr: DMR-0785462
	  budget:
	    - amount: 327595.0
	      begin_date: '2018-05-01'
	      end_date: '2018-09-30'
	      postdoc_months: 0.0
	      ss_months: 6.0
	      student_months: 12.0
	    - amount: 327595.0
	      begin_date: '2018-10-01'
	      end_date: '2019-01-30'
	      postdoc_months: 0.0
	      ss_months: 12.0
	      student_months: 8.0
	    - amount: 327595.0
	      begin_date: '2019-02-01'
	      end_date: '2019-05-01'
	      postdoc_months: 0.0
	      ss_months: 6.0
	      student_months: 12.0
	  funder: NSF
	  grant_id: DMREF-1534910
	  institution: Columbia University
	  notes: Designing Materials to Revolutionize and Engineer our Future (DMREF)
	  person_months_academic: 0.0
	  person_months_summer: 0.25
	  program: DMREF
	  proposal_id: dmref15
	  scope: This grant is to develop complex modeling methods for regularizing ill-posed
	    nanostructure inverse problems using data analytic and machine learning based
	    approaches. This does not overlap with any other grant.
	  team:
	    - institution: Columbia University
	      name: qdu
	      position: copi
	    - institution: Columbia University
	      name: dhsu
	      position: copi
	    - institution: Columbia University
	      name: Anthony Scopatz
	      position: pi
	      subaward_amount: 330000.0
	  title: 'DMREF: Novel, data validated, nanostructure determination methods for accelerating
	    materials discovery'
	ta:
	  amount: 0.0
	  begin_date: '2020-06-01'
	  budget:
	    - amount: 0.0
	      begin_date: '2020-06-01'
	      end_date: '2020-08-30'
	      postdoc_months: 0.0
	      ss_months: 0.0
	      student_months: 0.0
	  end_date: '2020-12-31'
	  funder: Life
	  program: Underground Grants
	  team:
	    - institution: Ministry of Magic
	      name: Chief Witch
	      position: pi
	    - institution: Ministry of Magic
	      name: Chief Wizard
	      position: copi
	  title: Support for teaching assistants


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "SymPy-1.1",
	    "admin": "APAM",
	    "alias": "sym",
	    "amount": 3000.0,
	    "awardnr": "NF-1234",
	    "begin_day": 1,
	    "begin_month": "May",
	    "begin_year": 2030,
	    "budget": [
	        {
	            "amount": 1000.0,
	            "begin_date": "2030-05-01",
	            "end_date": "2030-06-30",
	            "postdoc_months": 0.0,
	            "ss_months": 1.0,
	            "student_months": 0.5
	        },
	        {
	            "amount": 1000.0,
	            "begin_date": "2030-07-01",
	            "end_date": "2030-09-30",
	            "postdoc_months": 0.0,
	            "ss_months": 2.0,
	            "student_months": 1.5
	        },
	        {
	            "amount": 1000.0,
	            "begin_date": "2030-10-01",
	            "end_date": "2030-12-31",
	            "postdoc_months": 0.0,
	            "ss_months": 0.0,
	            "student_months": 3.0
	        }
	    ],
	    "call_for_proposals": "https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
	    "end_day": 31,
	    "end_month": "December",
	    "end_year": 2030,
	    "funder": "NumFOCUS",
	    "funds_available": [
	        {
	            "date": "2020-04-01",
	            "funds_available": 2800.0
	        },
	        {
	            "date": "2021-01-03",
	            "funds_available": 2100.0
	        },
	        {
	            "date": "2020-07-21",
	            "funds_available": 2600.0
	        }
	    ],
	    "narrative": "https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing",
	    "program": "Small Development Grants",
	    "team": [
	        {
	            "institution": "University of South Carolina",
	            "name": "Anthony Scopatz",
	            "position": "pi"
	        },
	        {
	            "admin_people": [
	                "A. D. Ministrator"
	            ],
	            "institution": "University of South Carolina",
	            "name": "Aaron Meurer",
	            "position": "researcher"
	        }
	    ],
	    "title": "SymPy 1.1 Release Support"
	}
	{
	    "_id": "SymPy-2.0",
	    "admin": "APAM",
	    "alias": "sym2.0",
	    "amount": 3000.0,
	    "awardnr": "NF-1234",
	    "begin_day": 1,
	    "begin_month": 6,
	    "begin_year": 2019,
	    "call_for_proposals": "https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
	    "end_day": 31,
	    "end_month": "December",
	    "end_year": 2030,
	    "funder": "NumFOCUS",
	    "funds_available": [
	        {
	            "date": "2020-04-01",
	            "funds_available": 2800.0
	        },
	        {
	            "date": "2021-01-03",
	            "funds_available": 2100.0
	        },
	        {
	            "date": "2020-07-21",
	            "funds_available": 2600.0
	        }
	    ],
	    "highlights": [
	        {
	            "description": "high profile pub in Nature",
	            "month": 5,
	            "year": 2020
	        }
	    ],
	    "narrative": "https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing",
	    "program": "Small Development Grants",
	    "proposal_id": "SymPy-2.0",
	    "status": "accepted",
	    "team": [
	        {
	            "institution": "University of South Carolina",
	            "name": "Anthony Scopatz",
	            "position": "pi"
	        },
	        {
	            "institution": "University of South Carolina",
	            "name": "Aaron Meurer",
	            "position": "researcher"
	        }
	    ],
	    "title": "SymPy 2.0 Release Support"
	}
	{
	    "_id": "abc42",
	    "alias": "abc42",
	    "amount": 42000.0,
	    "begin_date": "2020-06-01",
	    "budget": [
	        {
	            "amount": 42000.0,
	            "begin_date": "2020-06-01",
	            "end_date": "2020-12-31",
	            "postdoc_months": 0.0,
	            "ss_months": 1.0,
	            "student_months": 0.0
	        }
	    ],
	    "end_date": "2020-12-31",
	    "funder": "Life",
	    "program": "Metaphysical Grants",
	    "proposal_id": "abc42",
	    "team": [
	        {
	            "institution": "University of Pedagogy",
	            "name": "Chief Pedagogue",
	            "position": "pi"
	        },
	        {
	            "institution": "University of Pedagogy",
	            "name": "Pedagogue Jr.",
	            "position": "copi"
	        }
	    ],
	    "title": "The answer to life, the universe, and everything"
	}
	{
	    "_id": "dmref15",
	    "account": "GG012345",
	    "admin": "DSI",
	    "alias": "dmref15",
	    "amount": 982785.0,
	    "awardnr": "DMR-0785462",
	    "budget": [
	        {
	            "amount": 327595.0,
	            "begin_date": "2018-05-01",
	            "end_date": "2018-09-30",
	            "postdoc_months": 0.0,
	            "ss_months": 6.0,
	            "student_months": 12.0
	        },
	        {
	            "amount": 327595.0,
	            "begin_date": "2018-10-01",
	            "end_date": "2019-01-30",
	            "postdoc_months": 0.0,
	            "ss_months": 12.0,
	            "student_months": 8.0
	        },
	        {
	            "amount": 327595.0,
	            "begin_date": "2019-02-01",
	            "end_date": "2019-05-01",
	            "postdoc_months": 0.0,
	            "ss_months": 6.0,
	            "student_months": 12.0
	        }
	    ],
	    "funder": "NSF",
	    "grant_id": "DMREF-1534910",
	    "institution": "Columbia University",
	    "notes": "Designing Materials to Revolutionize and Engineer our Future (DMREF)",
	    "person_months_academic": 0.0,
	    "person_months_summer": 0.25,
	    "program": "DMREF",
	    "proposal_id": "dmref15",
	    "scope": "This grant is to develop complex modeling methods for regularizing ill-posed nanostructure inverse problems using data analytic and machine learning based approaches. This does not overlap with any other grant.",
	    "team": [
	        {
	            "institution": "Columbia University",
	            "name": "qdu",
	            "position": "copi"
	        },
	        {
	            "institution": "Columbia University",
	            "name": "dhsu",
	            "position": "copi"
	        },
	        {
	            "institution": "Columbia University",
	            "name": "Anthony Scopatz",
	            "position": "pi",
	            "subaward_amount": 330000.0
	        }
	    ],
	    "title": "DMREF: Novel, data validated, nanostructure determination methods for accelerating materials discovery"
	}
	{
	    "_id": "ta",
	    "amount": 0.0,
	    "begin_date": "2020-06-01",
	    "budget": [
	        {
	            "amount": 0.0,
	            "begin_date": "2020-06-01",
	            "end_date": "2020-08-30",
	            "postdoc_months": 0.0,
	            "ss_months": 0.0,
	            "student_months": 0.0
	        }
	    ],
	    "end_date": "2020-12-31",
	    "funder": "Life",
	    "program": "Underground Grants",
	    "team": [
	        {
	            "institution": "Ministry of Magic",
	            "name": "Chief Witch",
	            "position": "pi"
	        },
	        {
	            "institution": "Ministry of Magic",
	            "name": "Chief Wizard",
	            "position": "copi"
	        }
	    ],
	    "title": "Support for teaching assistants"
	}

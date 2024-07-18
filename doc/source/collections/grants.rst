Grants
======
This collection represents grants that have been awarded to the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ('string', 'integer', 'float'), short representation, such as this-is-my-name, required
:account: string, the account number which holds the funds, optional
:admin: string, the group administering the grant, optional
:amount: ('integer', 'float'), value of award, required
:begin_day: integer, start day of the grant, optional
:begin_month: ['string', 'integer'], start month of the grant, required
:begin_year: integer, start year of the grant, required
:benefit_of_collaboration: string, optional
:call_for_proposals: string, optional
:currency: string, typically '$' or 'USD', optional
:end_day: ('string', 'integer'), end day of the grant, optional
:end_month: ['string', 'integer'], end month of the grant, optional
:end_year: integer, end year of the grant, required
:funder: string, the agency funding the work, required
:grant_id: string, the identifier for this work, optional
:institution: string, the host institution for the grant, optional
:narrative: string, optional
:notes: string, notes about the grant, optional
:person_months_academic: ['integer', 'float'], Number of months of funding during the academicyear, optional
:person_months_summer: ['integer', 'float'], Number of months of funding during the summer, optional
:program: string, the program the work was funded under, required
:scope: string, The scope of the grant, answers the prompt: "Describe Research Including Synergies and Delineation with Respect to this Proposal/Award:", optional
:status: string, status of the grant, optional

	Allowed values: 
		* pending
		* declined
		* accepted
		* in-prep
:team: list, information about the team members participating in the grant., required

	:type: dict, optional

		:cv: string, optional
		:institution: string, optional
		:name: string, optional
		:position: string, optional
		:subaward_amount: ('integer', 'float'), optional
:title: string, actual title of proposal / grant, required


YAML Example
------------

.. code-block:: yaml

	SymPy-1.1:
	  amount: 3000.0
	  begin_day: 1
	  begin_month: May
	  begin_year: 2030
	  call_for_proposals: https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ
	  end_day: 31
	  end_month: December
	  end_year: 2030
	  funder: NumFOCUS
	  narrative: https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing
	  program: Small Development Grants
	  status: pending
	  team:
	    - institution: University of South Carolina
	      name: Anthony Scopatz
	      position: PI
	    - institution: University of South Carolina
	      name: Aaron Meurer
	      position: researcher
	  title: SymPy 1.1 Release Support
	dmref15:
	  account: GG012345
	  amount: 982785.0
	  begin_day: 1
	  begin_month: october
	  begin_year: 2015
	  end_day: 30
	  end_month: september
	  end_year: 2025
	  funder: NSF
	  grant_id: DMREF-1534910
	  institution: Columbia University
	  notes: Designing Materials to Revolutionize and Engineer our Future (DMREF)
	  person_months_academic: 0.0
	  person_months_summer: 0.25
	  program: DMREF
	  scope: This grant is to develop complex modeling methods for regularizing ill-posed
	    nanostructure inverse problems using data analytic and machine learning based
	    approaches. This does not overlap with any other grant.
	  team:
	    - institution: Columbia University
	      name: qdu
	      position: Co-PI
	    - institution: Columbia University
	      name: dhsu
	      position: Co-PI
	    - institution: Columbia University
	      name: Anthony Scopatz
	      position: PI
	      subaward_amount: 330000.0
	  title: 'DMREF: Novel, data validated, nanostructure determination methods for accelerating
	    materials discovery'


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "SymPy-1.1",
	    "amount": 3000.0,
	    "begin_day": 1,
	    "begin_month": "May",
	    "begin_year": 2030,
	    "call_for_proposals": "https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
	    "end_day": 31,
	    "end_month": "December",
	    "end_year": 2030,
	    "funder": "NumFOCUS",
	    "narrative": "https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing",
	    "program": "Small Development Grants",
	    "status": "pending",
	    "team": [
	        {
	            "institution": "University of South Carolina",
	            "name": "Anthony Scopatz",
	            "position": "PI"
	        },
	        {
	            "institution": "University of South Carolina",
	            "name": "Aaron Meurer",
	            "position": "researcher"
	        }
	    ],
	    "title": "SymPy 1.1 Release Support"
	}
	{
	    "_id": "dmref15",
	    "account": "GG012345",
	    "amount": 982785.0,
	    "begin_day": 1,
	    "begin_month": "october",
	    "begin_year": 2015,
	    "end_day": 30,
	    "end_month": "september",
	    "end_year": 2025,
	    "funder": "NSF",
	    "grant_id": "DMREF-1534910",
	    "institution": "Columbia University",
	    "notes": "Designing Materials to Revolutionize and Engineer our Future (DMREF)",
	    "person_months_academic": 0.0,
	    "person_months_summer": 0.25,
	    "program": "DMREF",
	    "scope": "This grant is to develop complex modeling methods for regularizing ill-posed nanostructure inverse problems using data analytic and machine learning based approaches. This does not overlap with any other grant.",
	    "team": [
	        {
	            "institution": "Columbia University",
	            "name": "qdu",
	            "position": "Co-PI"
	        },
	        {
	            "institution": "Columbia University",
	            "name": "dhsu",
	            "position": "Co-PI"
	        },
	        {
	            "institution": "Columbia University",
	            "name": "Anthony Scopatz",
	            "position": "PI",
	            "subaward_amount": 330000.0
	        }
	    ],
	    "title": "DMREF: Novel, data validated, nanostructure determination methods for accelerating materials discovery"
	}

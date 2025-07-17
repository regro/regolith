Proposals
=========
This collection represents proposals that have been submitted by the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ['string', 'integer', 'float'], short representation, such as this-is-my-name, required
:amount: ['integer', 'float'], value of award, required
:authors: ['list', 'string'], other investigator names, optional
:begin_date: ['string', 'date'], start date of the proposed grant in format YYYY-MM-DD, optional
:begin_day: integer, start day of the proposed grant, optional
:begin_month: ['string', 'integer'], start month of the proposed grant, optional
:begin_year: integer, start year of the proposed grant, optional
:call_for_proposals: string, optional
:cpp_info: dict, extra information needed for building current and pending form , optional

	:cppflag: boolean, optional
	:other_agencies_submitted: ['string', 'boolean'], optional
	:institution: string, place where the proposed grant will be located, optional
	:person_months_academic: ['float', 'integer'], optional
	:person_months_summer: ['float', 'integer'], optional
	:project_scope: string, optional
	:single_pi: boolean, set to true if there are no co-pi's, optional
:currency: string, typically '$' or 'USD', required
:due_date: ['string', 'date'], day that the proposal is due, optional
:duration: ['integer', 'float'], number of years, optional
:end_date: ['string', 'date'], end date of the proposed grant in format YYYY-MM-DD, optional
:end_day: ['string', 'integer'], end day of the proposed grant, optional
:end_month: ['string', 'integer'], end month of the proposed grant, optional
:end_year: integer, end year of the proposed grant, optional
:full: dict, full body of the proposal, optional
:funder: string, who will fund the proposalas funder in grants, optional
:notes: ['string', 'list'], anything you want to note, optional
:pi: string, principal investigator name, required
:pre: dict, Information about the pre-proposal, optional
:status: string, e.g. 'pending', 'accepted', 'declined', required

	Allowed values:
		* pending
		* declined
		* accepted
		* inprep
		* submitted
:submitted_date: ['string', 'date'], date that the proposal was submitted, optional
:submitted_day: integer, day that the proposal was submitted, optional
:submitted_month: ['string', 'integer'], month that the proposal was submitted, optional
:submitted_year: integer, Year that the proposal was submitted, optional
:team: list, information about the team members participating in the grant., optional

	:type: dict, optional

		:cv: string, optional
		:email: string, optional
		:institution: string, optional
		:name: string, optional
		:position: string, optional
		:subaward_amount: ['integer', 'float'], optional
:title: string, actual title of proposal, required
:title_short: string, short title of proposal, optional


YAML Example
------------

.. code-block:: yaml

	SymPy-1.1:
	  amount: 3000.0
	  begin_date: '2030-05-01'
	  cpp_info:
	    cppflag: true
	    institution: Columbia University
	    other_agencies_submitted: None
	    person_months_academic: 0
	    person_months_summer: 1
	    project_scope: ''
	  currency: USD
	  end_date: '2030-12-31'
	  pi: Anthony Scopatz
	  status: pending
	  team:
	    - institution: Columbia University
	      name: scopatz
	      position: pi
	  title: SymPy 1.1 Release Support
	SymPy-2.1:
	  amount: 3000.0
	  begin_date: '2019-06-01'
	  cpp_info:
	    cppflag: true
	    institution: Columbia University
	    other_agencies_submitted: None
	    person_months_academic: 0
	    person_months_summer: 1
	    project_scope: ''
	  currency: USD
	  end_date: '2030-12-31'
	  pi: sbillinge
	  status: accepted
	  team:
	    - institution: University of 2.1
	      name: Anthony Scopatz 2.1
	      position: pi
	  title: SymPy 2.1 Release Support
	abc42:
	  amount: 42000.0
	  begin_date: '2020-06-01'
	  cpp_info:
	    cppflag: true
	    institution: Columbia University
	    other_agencies_submitted: None
	    person_months_academic: 0
	    person_months_summer: 1
	    project_scope: ''
	  currency: USD
	  end_date: '2020-12-31'
	  pi: sbillinge
	  status: submitted
	  title: The answer to life, the universe, and everything
	dmref15:
	  amount: 982785.0
	  authors:
	    - qdu
	    - dhsu
	    - sbillinge
	  begin_day: 1
	  begin_month: May
	  begin_year: 2018
	  call_for_proposals: http://www.nsf.gov/pubs/2014/nsf14591/nsf14591.htm
	  cpp_info:
	    cppflag: true
	    institution: Columbia University
	    other_agencies_submitted: None
	    person_months_academic: 0
	    person_months_summer: 1
	    project_scope: lots to do but it doesn't overlap with any other of my grants
	    single_pi: true
	  currency: USD
	  duration: 3
	  end_day: 1
	  end_month: May
	  end_year: 2019
	  funder: NSF
	  notes: Quite an idea
	  pi: Simon Billinge
	  status: accepted
	  submitted_date: '2015-02-02'
	  team:
	    - institution: Columbia University
	      name: qdu
	      position: copi
	    - institution: Columbia University
	      name: dhsu
	      position: copi
	    - institution: Columbia University
	      name: sbillinge
	      position: pi
	      subaward_amount: 330000.0
	  title: 'DMREF: Novel, data validated, nanostructure determination methods for accelerating
	    materials discovery'
	  title_short: DMREF nanostructure
	mypropsal:
	  amount: 1000000.0
	  authors:
	    - Anthony Scopatz
	    - Robert Flanagan
	  begin_day: 1
	  begin_month: May
	  begin_year: 2030
	  currency: USD
	  duration: 3
	  end_day: 31
	  end_month: December
	  end_year: 2030
	  full:
	    benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
	    cv:
	      - http://pdf.com/scopatz-cv
	      - http://pdf.com/flanagan-cv
	    narrative: http://some.com/pdf
	  notes: Quite an idea
	  pi: Anthony Scopatz
	  pre:
	    benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
	    cv:
	      - http://pdf.com/scopatz-cv
	      - http://pdf.com/flanagan-cv
	    day: 2
	    month: Aug
	    narrative: http://some.com/pdf
	    year: 1998
	  status: submitted
	  submitted_day: 18
	  submitted_month: Aug
	  submitted_year: 1999
	  title: A very fine proposal indeed


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "SymPy-1.1",
	    "amount": 3000.0,
	    "begin_date": "2030-05-01",
	    "cpp_info": {
	        "cppflag": true,
	        "institution": "Columbia University",
	        "other_agencies_submitted": "None",
	        "person_months_academic": 0,
	        "person_months_summer": 1,
	        "project_scope": ""
	    },
	    "currency": "USD",
	    "end_date": "2030-12-31",
	    "pi": "Anthony Scopatz",
	    "status": "pending",
	    "team": [
	        {
	            "institution": "Columbia University",
	            "name": "scopatz",
	            "position": "pi"
	        }
	    ],
	    "title": "SymPy 1.1 Release Support"
	}
	{
	    "_id": "SymPy-2.1",
	    "amount": 3000.0,
	    "begin_date": "2019-06-01",
	    "cpp_info": {
	        "cppflag": true,
	        "institution": "Columbia University",
	        "other_agencies_submitted": "None",
	        "person_months_academic": 0,
	        "person_months_summer": 1,
	        "project_scope": ""
	    },
	    "currency": "USD",
	    "end_date": "2030-12-31",
	    "pi": "sbillinge",
	    "status": "accepted",
	    "team": [
	        {
	            "institution": "University of 2.1",
	            "name": "Anthony Scopatz 2.1",
	            "position": "pi"
	        }
	    ],
	    "title": "SymPy 2.1 Release Support"
	}
	{
	    "_id": "abc42",
	    "amount": 42000.0,
	    "begin_date": "2020-06-01",
	    "cpp_info": {
	        "cppflag": true,
	        "institution": "Columbia University",
	        "other_agencies_submitted": "None",
	        "person_months_academic": 0,
	        "person_months_summer": 1,
	        "project_scope": ""
	    },
	    "currency": "USD",
	    "end_date": "2020-12-31",
	    "pi": "sbillinge",
	    "status": "submitted",
	    "title": "The answer to life, the universe, and everything"
	}
	{
	    "_id": "dmref15",
	    "amount": 982785.0,
	    "authors": [
	        "qdu",
	        "dhsu",
	        "sbillinge"
	    ],
	    "begin_day": 1,
	    "begin_month": "May",
	    "begin_year": 2018,
	    "call_for_proposals": "http://www.nsf.gov/pubs/2014/nsf14591/nsf14591.htm",
	    "cpp_info": {
	        "cppflag": true,
	        "institution": "Columbia University",
	        "other_agencies_submitted": "None",
	        "person_months_academic": 0,
	        "person_months_summer": 1,
	        "project_scope": "lots to do but it doesn't overlap with any other of my grants",
	        "single_pi": true
	    },
	    "currency": "USD",
	    "duration": 3,
	    "end_day": 1,
	    "end_month": "May",
	    "end_year": 2019,
	    "funder": "NSF",
	    "notes": "Quite an idea",
	    "pi": "Simon Billinge",
	    "status": "accepted",
	    "submitted_date": "2015-02-02",
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
	            "name": "sbillinge",
	            "position": "pi",
	            "subaward_amount": 330000.0
	        }
	    ],
	    "title": "DMREF: Novel, data validated, nanostructure determination methods for accelerating materials discovery",
	    "title_short": "DMREF nanostructure"
	}
	{
	    "_id": "mypropsal",
	    "amount": 1000000.0,
	    "authors": [
	        "Anthony Scopatz",
	        "Robert Flanagan"
	    ],
	    "begin_day": 1,
	    "begin_month": "May",
	    "begin_year": 2030,
	    "currency": "USD",
	    "duration": 3,
	    "end_day": 31,
	    "end_month": "December",
	    "end_year": 2030,
	    "full": {
	        "benefit_of_collaboration": "http://pdf.com/benefit_of_collaboration",
	        "cv": [
	            "http://pdf.com/scopatz-cv",
	            "http://pdf.com/flanagan-cv"
	        ],
	        "narrative": "http://some.com/pdf"
	    },
	    "notes": "Quite an idea",
	    "pi": "Anthony Scopatz",
	    "pre": {
	        "benefit_of_collaboration": "http://pdf.com/benefit_of_collaboration",
	        "cv": [
	            "http://pdf.com/scopatz-cv",
	            "http://pdf.com/flanagan-cv"
	        ],
	        "day": 2,
	        "month": "Aug",
	        "narrative": "http://some.com/pdf",
	        "year": 1998
	    },
	    "status": "submitted",
	    "submitted_day": 18,
	    "submitted_month": "Aug",
	    "submitted_year": 1999,
	    "title": "A very fine proposal indeed"
	}

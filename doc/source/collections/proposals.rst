Proposals
=========
This collection represents proposals that have been submitted by the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ('string', 'integer', 'float'), short representation, such as this-is-my-name, required
:amount: ('integer', 'float'), value of award, required
:authors: ['list', 'string'], other investigator names, required
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
:currency: string, typically '$' or 'USD', required
:day: integer, day that the proposal was submitted, required
:due_date: string, day that the proposal is due, optional
:duration: ('integer', 'float'), number of years, required
:end_day: ('string', 'integer'), end day of the proposed grant, optional
:end_month: ['string', 'integer'], end month of the proposed grant, optional
:end_year: integer, end year of the proposed grant, optional
:full: dict, full body of the proposal, optional
:funder: string, who will fund the proposalas funder in grants, optional
:month: ['string', 'integer'], month that the proposal was submitted, required
:notes: ['string', 'list'], anything you want to note, optional
:pi: string, principal investigator name, required
:pre: dict, Information about the pre-proposal, optional
:status: string, e.g. 'pending', 'accepted', 'rejected', required

	Allowed values: 
		* pending
		* declined
		* accepted
		* in-prep
		* submitted
:team: list, information about the team members participating in the grant., optional

	:type: dict, optional

		:cv: string, optional
		:email: string, optional
		:institution: string, optional
		:name: string, optional
		:position: string, optional
		:subaward_amount: ('integer', 'float'), optional
:title: string, actual title of proposal, required
:title_short: string, short title of proposal, optional
:year: integer, Year that the proposal was submitted, required


YAML Example
------------

.. code-block:: yaml

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
	  currency: USD
	  day: 2
	  duration: 3
	  end_day: 1
	  end_month: May
	  end_year: 2019
	  funder: NSF
	  month: february
	  notes: Quite an idea
	  pi: Simon Billinge
	  status: accepted
	  team:
	    - institution: Columbia Unviersity
	      name: qdu
	      position: Co-PI
	    - institution: Columbia Unviersity
	      name: dhsu
	      position: Co-PI
	    - institution: Columbia Unviersity
	      name: sbillinge
	      position: PI
	      subaward_amount: 330000.0
	  title: 'DMREF: Novel, data validated, nanostructure determination methods for accelerating
	    materials discovery'
	  title_short: DMREF nanostructure
	  year: 2015
	mypropsal:
	  amount: 1000000.0
	  authors:
	    - Anthony Scopatz
	    - Robert Flanagan
	  begin_day: 1
	  begin_month: May
	  begin_year: 2030
	  currency: USD
	  day: 18
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
	  month: Aug
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
	  title: A very fine proposal indeed
	  year: 1999


JSON/Mongo Example
------------------

.. code-block:: json

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
	        "project_scope": "lots to do but it doesn't overlap with any other of my grants"
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
	            "institution": "Columbia Unviersity",
	            "name": "qdu",
	            "position": "Co-PI"
	        },
	        {
	            "institution": "Columbia Unviersity",
	            "name": "dhsu",
	            "position": "Co-PI"
	        },
	        {
	            "institution": "Columbia Unviersity",
	            "name": "sbillinge",
	            "position": "PI",
	            "subaward_amount": 330000.0
	        }
	    ],
	    "title": "DMREF: Novel, data validated, nanostructure determination methods for accelerating materials discovery",
	    "title_short": "DMREF nanostructure",
	    "year": 2015
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
	    "day": 18,
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
	    "month": "Aug",
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
	    "title": "A very fine proposal indeed",
	    "year": 1999
	}

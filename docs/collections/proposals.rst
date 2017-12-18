Proposals
=========
This collection represents proposals that have been submitted by the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ('string', 'integer', 'float'), short represntation, such as this-is-my-name, required
:ammount: ('integer', 'float'), value of award, required
:authors: string, other investigator names, required
:currency: string, typically '$' or 'USD', required
:day: integer, day that the proposal is due, required
:durration: ('integer', 'float'), number of years, required
:month: string, month that the proposal is due, required
:pi: string, principal investigator name, required
:pre: dict, Information about the pre-proposal, optional
:status: string, e.g. 'submitted', 'accepted', 'rejected', required
:title: string, actual title of proposal, required
:year: integer, Year that the proposal is due, required


YAML Example
------------

.. code-block:: yaml

	mypropsal:
	  durration: 3
	  pre:
	    cv:
	      - http://pdf.com/scopatz-cv
	      - http://pdf.com/flanagan-cv
	    narrative: http://some.com/pdf
	    month: Aug
	    benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
	    day: 2
	    year: 1998
	  month: Aug
	  status: submitted
	  day: 18
	  full:
	    narrative: http://some.com/pdf
	    cv:
	      - http://pdf.com/scopatz-cv
	      - http://pdf.com/flanagan-cv
	    benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
	  ammount: 1000000.0
	  pi: Anthony Scopatz
	  currency: USD
	  authors:
	    - Anthony Scopatz
	    - Robert Flanagan
	  year: 1999
	  title: A very fine proposal indeed


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "mypropsal",
	    "ammount": 1000000.0,
	    "authors": [
	        "Anthony Scopatz",
	        "Robert Flanagan"
	    ],
	    "currency": "USD",
	    "day": 18,
	    "durration": 3,
	    "full": {
	        "benefit_of_collaboration": "http://pdf.com/benefit_of_collaboration",
	        "cv": [
	            "http://pdf.com/scopatz-cv",
	            "http://pdf.com/flanagan-cv"
	        ],
	        "narrative": "http://some.com/pdf"
	    },
	    "month": "Aug",
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

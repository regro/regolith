Refereereports
==============
This is a collection of information that will be be used to build a referee report. This should probably be private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, the ID, required
:claimed_found_what: list, What the authors claim to have found, required

	:type: string, required
:claimed_why_important: list, What importance the authors claim, required

	:type: string, required
:did_how: list, How the study was done, required

	:type: string, required
:did_what: list, What the study was, required

	:type: string, required
:due_date: ['string', 'date'], date the review is due in ISO format, required
:editor_eyes_only: string, Comments you don't want passed to the author, optional
:final_assessment: list, Summary of impressions of the study, required

	:type: string, required
:first_author_last_name: string, Last name of first author will be referred to with et al., required
:freewrite: string, Things that you want to add that don't fit into any category above, optional
:institutions: ['string', 'list'], the institutions of the pi and co-pis, optional
:journal: string, name of the journal, required
:month: ['integer', 'string'], The month the review was requested, optional
:recommendation: string, Your publication recommendation, required

	Allowed values:
		* reject
		* asis
		* smalledits
		* diffjournal
		* majoredits
:requester: string, Name of the program officer who requested the review, required
:reviewer: string, name of person reviewing the paper, required
:status: string, Where you are with the review, required

	Allowed values:
		* invited
		* accepted
		* declined
		* downloaded
		* inprogress
		* submitted
		* cancelled
:submitted_date: ['string', 'date'], submitted date in ISO YYYY-MM-DD format., optional
:title: string, title of the paper under review, required
:validity_assessment: list, List of impressions of the validity of the claims, required

	:type: string, required
:year: ['string', 'integer'], year when the review is being done, required


YAML Example
------------

.. code-block:: yaml

	1902nature:
	  claimed_found_what:
	    - gravity waves
	  claimed_why_important:
	    - more money for ice cream
	  did_how:
	    - measured with a ruler
	  did_what:
	    - found a much cheaper way to measure gravity waves
	  due_date: '2020-04-11'
	  editor_eyes_only: to be honest, I don't believe a word of it
	  final_assessment:
	    - The authors should really start over
	  first_author_last_name: Wingit
	  freewrite: this comment didn't fit anywhere above
	  journal: Nature
	  month: jun
	  recommendation: reject
	  requester: Max Planck
	  reviewer: sbillinge
	  status: submitted
	  submitted_date: '2019-01-01'
	  title: a ruler approach to measuring gravity waves
	  validity_assessment:
	    - complete rubbish
	  year: 2019
	2002nature:
	  claimed_found_what:
	    - more gravity waves
	  claimed_why_important:
	    - even more money for ice cream
	  did_how:
	    - measured with a ruler
	  did_what:
	    - found an even cheaper way to measure gravity waves
	  due_date: '2021-04-11'
	  editor_eyes_only: to be honest, I don't believe a word of it
	  final_assessment:
	    - The authors should really start over
	  first_author_last_name: Wingit
	  freewrite: this comment didn't fit anywhere above
	  journal: Nature
	  month: jun
	  recommendation: reject
	  requester: Max Planck
	  reviewer: sbillinge
	  status: accepted
	  submitted_date: '2020-01-01'
	  title: an even smaller ruler approach to measuring gravity waves
	  validity_assessment:
	    - complete rubbish
	  year: 2020


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "1902nature",
	    "claimed_found_what": [
	        "gravity waves"
	    ],
	    "claimed_why_important": [
	        "more money for ice cream"
	    ],
	    "did_how": [
	        "measured with a ruler"
	    ],
	    "did_what": [
	        "found a much cheaper way to measure gravity waves"
	    ],
	    "due_date": "2020-04-11",
	    "editor_eyes_only": "to be honest, I don't believe a word of it",
	    "final_assessment": [
	        "The authors should really start over"
	    ],
	    "first_author_last_name": "Wingit",
	    "freewrite": "this comment didn't fit anywhere above",
	    "journal": "Nature",
	    "month": "jun",
	    "recommendation": "reject",
	    "requester": "Max Planck",
	    "reviewer": "sbillinge",
	    "status": "submitted",
	    "submitted_date": "2019-01-01",
	    "title": "a ruler approach to measuring gravity waves",
	    "validity_assessment": [
	        "complete rubbish"
	    ],
	    "year": 2019
	}
	{
	    "_id": "2002nature",
	    "claimed_found_what": [
	        "more gravity waves"
	    ],
	    "claimed_why_important": [
	        "even more money for ice cream"
	    ],
	    "did_how": [
	        "measured with a ruler"
	    ],
	    "did_what": [
	        "found an even cheaper way to measure gravity waves"
	    ],
	    "due_date": "2021-04-11",
	    "editor_eyes_only": "to be honest, I don't believe a word of it",
	    "final_assessment": [
	        "The authors should really start over"
	    ],
	    "first_author_last_name": "Wingit",
	    "freewrite": "this comment didn't fit anywhere above",
	    "journal": "Nature",
	    "month": "jun",
	    "recommendation": "reject",
	    "requester": "Max Planck",
	    "reviewer": "sbillinge",
	    "status": "accepted",
	    "submitted_date": "2020-01-01",
	    "title": "an even smaller ruler approach to measuring gravity waves",
	    "validity_assessment": [
	        "complete rubbish"
	    ],
	    "year": 2020
	}

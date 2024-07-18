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
:editor_eyes_only: string, Comments you don't want passed to the author, optional
:final_assessment: list, Summary of impressions of the study, required

	:type: string, required
:first_author_last_name: string, Last name of first author will be referred to with et al., required
:freewrite: string, Things that you want to add that don't fit into any category above, optional
:journal: string, name of the journal, required
:month: ['string', 'integer'], month when the review is being written, required
:recommendation: string, Your publication recommendation, required

	Allowed values: 
		* reject
		* asis
		* smalledits
		* diffjournal
		* majoredits
:reviewer: string, name of person reviewing the paper, required
:status: string, Where you are with the review, required

	Allowed values: 
		* accepted
		* declined
		* downloaded
		* inprogress
		* submitted
:title: string, title of the paper under review, required
:validity_assessment: list, List of impressions of the validity of the claims, required

	:type: string, required
:year: string, year when the review is being done, required


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
	  editor_eyes_only: to be honest, I don't believe a word of it
	  final_assessment:
	    - The authors should really start over
	  first_author_last_name: Wingit
	  freewrite: this comment didn't fit anywhere above
	  journal: Nature
	  month: 2
	  recommendation: reject
	  reviewer: sbillinge
	  status: submitted
	  title: a ruler approach to measuring gravity waves
	  validity_assessment:
	    - complete rubbish
	  year: '2019'


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
	    "editor_eyes_only": "to be honest, I don't believe a word of it",
	    "final_assessment": [
	        "The authors should really start over"
	    ],
	    "first_author_last_name": "Wingit",
	    "freewrite": "this comment didn't fit anywhere above",
	    "journal": "Nature",
	    "month": 2,
	    "recommendation": "reject",
	    "reviewer": "sbillinge",
	    "status": "submitted",
	    "title": "a ruler approach to measuring gravity waves",
	    "validity_assessment": [
	        "complete rubbish"
	    ],
	    "year": "2019"
	}

Presentations
=============
This collection describes presentations that groupmembers make at conferences, symposia, seminars andso on.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique id for the presentation, required
:abstract: string, abstract of the presentation, optional
:authors: ['string', 'list'], Author list., required
:begin_day: integer, optional
:begin_month: ['string', 'integer'], required
:begin_year: integer, year the conference or trip begins., required
:department: string, department of the institution where thepresentation will be made, if applicable.  should be discoverable in institutions., optional
:end_day: integer, optional
:end_month: ['string', 'integer'], optional
:end_year: integer, year the conference or trip ends, optional
:institution: string, institution where thepresentation will be made, if applicable., optional
:location: string, city and {state or country} of meeting, optional
:meeting_name: string, full name of the conference or meeting.  If it is a departmental seminar or colloquium, write Seminaror Colloquium and fill in department and institution fields, optional
:notes: ['list', 'string'], any reminder or memory aid about anything, optional
:project: ['string', 'list'], project or list of projects that this presentation is associated with.  Should be discoverable in projects collection, optional
:status: string, Is the application in prep or submitted, was the invitation accepted or declined, was the trip cancelled?, required

	Allowed values: 
		* in-prep
		* submitted
		* accepted
		* declined
		* cancelled
:title: string, title of the presentation, required
:type: string, type of presentation, required

	Allowed values: 
		* award
		* colloquium
		* contributed_oral
		* invited
		* keynote
		* plenary
		* poster
		* seminar


YAML Example
------------

.. code-block:: yaml

	18sb04_kentstate:
	  abstract: We made the case for local structure
	  authors:
	    - scopatz
	  begin_day: 22
	  begin_month: May
	  begin_year: 2018
	  department: physics
	  end_day: 22
	  end_month: 5
	  end_year: 2018
	  institution: columbiau
	  notes:
	    - what a week!
	  project: 18kj_conservation
	  status: accepted
	  title: Nanostructure challenges and successes from 16th Century warships to 21st
	    Century energy
	  type: colloquium
	18sb_nslsii:
	  abstract: We pulled apart graphite with tape
	  authors:
	    - scopatz
	  begin_day: 22
	  begin_month: 5
	  begin_year: 2018
	  department: apam
	  end_day: 22
	  end_month: 5
	  end_year: 2018
	  institution: columbiau
	  location: Upton NY
	  meeting_name: 2018 NSLS-II and CFN Users Meeting
	  notes:
	    - We hope the weather will be sunny
	    - if the weather is nice we will go to the beach
	  project: 18sob_clustermining
	  status: accepted
	  title: 'ClusterMining: extracting core structures of metallic nanoparticles from
	    the atomic pair distribution function'
	  type: poster
	18sb_this_and_that:
	  abstract: We pulled apart graphite with tape
	  authors:
	    - scopatz
	  begin_day: 22
	  begin_month: 5
	  begin_year: 2018
	  department: apam
	  institution: columbiau
	  location: Upton NY
	  meeting_name: Meeting to check flexibility on dates
	  notes:
	    - We hope the weather will be sunny
	    - if the weather is nice we will go to the beach
	  project: 18sob_clustermining
	  status: accepted
	  title: Graphitic Dephenestration
	  type: award


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "18sb04_kentstate",
	    "abstract": "We made the case for local structure",
	    "authors": [
	        "scopatz"
	    ],
	    "begin_day": 22,
	    "begin_month": "May",
	    "begin_year": 2018,
	    "department": "physics",
	    "end_day": 22,
	    "end_month": 5,
	    "end_year": 2018,
	    "institution": "columbiau",
	    "notes": [
	        "what a week!"
	    ],
	    "project": "18kj_conservation",
	    "status": "accepted",
	    "title": "Nanostructure challenges and successes from 16th Century warships to 21st Century energy",
	    "type": "colloquium"
	}
	{
	    "_id": "18sb_nslsii",
	    "abstract": "We pulled apart graphite with tape",
	    "authors": [
	        "scopatz"
	    ],
	    "begin_day": 22,
	    "begin_month": 5,
	    "begin_year": 2018,
	    "department": "apam",
	    "end_day": 22,
	    "end_month": 5,
	    "end_year": 2018,
	    "institution": "columbiau",
	    "location": "Upton NY",
	    "meeting_name": "2018 NSLS-II and CFN Users Meeting",
	    "notes": [
	        "We hope the weather will be sunny",
	        "if the weather is nice we will go to the beach"
	    ],
	    "project": "18sob_clustermining",
	    "status": "accepted",
	    "title": "ClusterMining: extracting core structures of metallic nanoparticles from the atomic pair distribution function",
	    "type": "poster"
	}
	{
	    "_id": "18sb_this_and_that",
	    "abstract": "We pulled apart graphite with tape",
	    "authors": [
	        "scopatz"
	    ],
	    "begin_day": 22,
	    "begin_month": 5,
	    "begin_year": 2018,
	    "department": "apam",
	    "institution": "columbiau",
	    "location": "Upton NY",
	    "meeting_name": "Meeting to check flexibility on dates",
	    "notes": [
	        "We hope the weather will be sunny",
	        "if the weather is nice we will go to the beach"
	    ],
	    "project": "18sob_clustermining",
	    "status": "accepted",
	    "title": "Graphitic Dephenestration",
	    "type": "award"
	}

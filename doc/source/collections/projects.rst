Projects
========
This collection describes the research group projects. This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique project identifier., required
:active: ['string', 'boolean'], true if the project is active, optional
:description: string, brief project description., required
:grants: list, Grant id if there is a grant supporting this project, optional

	:type: string, the list of ids/akas of grants related to this project, optional
	:description: string, the list of ids/akas of grants related to this project, optional
:group: string, id for the group in the groups collection whose project this is, optional
:highlights: list, list of things to highlight in a report or website, such as releases for  for software or high profile publications, optional

	:type: dict, optional

		:year: integer, the year of the highlight, optional
		:month: ['string', 'integer'], the month of the highlight, optional
		:description: string, the highlight, optional
:logo: string, URL to the project logo, optional
:name: string, name of the project., required
:other: ['list', 'string'], other information about the project, optional
:repo: string, URL of the source code repo, if available, optional
:summary: string, The summary of the project, optional
:team: list, People who are/have been working on this project., required

	:type: dict, optional

		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:name: string, optional
		:position: string, optional
:type: ['string'], The type of project, optional

	Allowed values:
		* ossoftware
		* funded
		* outreach
:website: string, URL of the website., optional


YAML Example
------------

.. code-block:: yaml

	Cyclus:
	  description: Agent-Based Nuclear Fuel Cycle Simulator
	  grants:
	    - dmref15
	  group: ergs
	  highlights:
	    - description: high profile pub in Nature
	      month: 5
	      year: 2020
	  logo: http://fuelcycle.org/_static/big_c.png
	  name: Cyclus
	  other:
	    - Discrete facilities with discrete material transactions
	    - Low barrier to entry, rapid payback to adoption
	  repo: https://github.com/cyclus/cyclus/
	  summary: In summary, a cool project
	  team:
	    - begin_month: June
	      begin_year: 2013
	      end_month: July
	      end_year: 2015
	      name: Anthony Scopatz
	      position: Project Lead
	  type: funded
	  website: http://fuelcycle.org/


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Cyclus",
	    "description": "Agent-Based Nuclear Fuel Cycle Simulator",
	    "grants": [
	        "dmref15"
	    ],
	    "group": "ergs",
	    "highlights": [
	        {
	            "description": "high profile pub in Nature",
	            "month": 5,
	            "year": 2020
	        }
	    ],
	    "logo": "http://fuelcycle.org/_static/big_c.png",
	    "name": "Cyclus",
	    "other": [
	        "Discrete facilities with discrete material transactions",
	        "Low barrier to entry, rapid payback to adoption"
	    ],
	    "repo": "https://github.com/cyclus/cyclus/",
	    "summary": "In summary, a cool project",
	    "team": [
	        {
	            "begin_month": "June",
	            "begin_year": 2013,
	            "end_month": "July",
	            "end_year": 2015,
	            "name": "Anthony Scopatz",
	            "position": "Project Lead"
	        }
	    ],
	    "type": "funded",
	    "website": "http://fuelcycle.org/"
	}

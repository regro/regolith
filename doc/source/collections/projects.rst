Projects
========
This collection describes the research group projects. This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique project identifier., required
:description: string, brief project description., required
:grant: string, Grant id if there is a grant supporting this project, optional
:logo: string, URL to the project logo, optional
:name: string, name of the project., required
:other: ['list', 'string'], other information about the project, optional
:repo: string, URL of the source code repo, if available, optional
:team: list, People who are/have been working on this project., required

	:type: dict, optional

		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:name: string, optional
		:position: string, optional
:website: string, URL of the website., required


YAML Example
------------

.. code-block:: yaml

	Cyclus:
	  description: Agent-Based Nuclear Fuel Cycle Simulator
	  grant: dmref15
	  logo: http://fuelcycle.org/_static/big_c.png
	  name: Cyclus
	  other:
	    - Discrete facilities with discrete material transactions
	    - Low barrier to entry, rapid payback to adoption
	  repo: https://github.com/cyclus/cyclus/
	  team:
	    - begin_month: June
	      begin_year: 2013
	      end_month: July
	      end_year: 2015
	      name: Anthony Scopatz
	      position: Project Lead
	  website: http://fuelcycle.org/


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Cyclus",
	    "description": "Agent-Based Nuclear Fuel Cycle Simulator",
	    "grant": "dmref15",
	    "logo": "http://fuelcycle.org/_static/big_c.png",
	    "name": "Cyclus",
	    "other": [
	        "Discrete facilities with discrete material transactions",
	        "Low barrier to entry, rapid payback to adoption"
	    ],
	    "repo": "https://github.com/cyclus/cyclus/",
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
	    "website": "http://fuelcycle.org/"
	}

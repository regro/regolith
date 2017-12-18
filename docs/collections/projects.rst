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
:team: list, People who are/have been woking on this project., required
	:end_month: string, optional
	:begin_year: integer, optional
	:end_year: integer, optional
	:position: string, optional
	:begin_month: string, optional
	:name: string, optional
:website: string, URL of the website., required


YAML Example
------------

.. code-block:: yaml

	Cyclus:
	  other:
	    - Discrete facilities with discrete material transactions
	    - Low barrier to entry, rapid payback to adoption
	  logo: http://fuelcycle.org/_static/big_c.png
	  website: http://fuelcycle.org/
	  description: Agent-Based Nuclear Fuel Cycle Simulator
	  team:
	    - end_month: July
	      begin_year: 2013
	      end_year: 2015
	      position: Project Lead
	      begin_month: June
	      name: Anthony Scopatz
	  repo: https://github.com/cyclus/cyclus/
	  name: Cyclus


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Cyclus",
	    "description": "Agent-Based Nuclear Fuel Cycle Simulator",
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

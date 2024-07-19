Institutions
============
This collection will contain all the institutionsin the world and their departments and addresses

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique identifier for the institution., required
:aka: list, list of all the different names this the institution is known by, optional
:city: string, the city where the institution is, required
:country: string, The country where the institution is, required
:date: ['string', 'date'], Expense date, optional
:day: integer, the day the entry was created, optional
:departments: dict, all the departments and centers andvarious units in the institution, optional
:month: ['string', 'integer'], the month the entry was created, optional
:name: string, the canonical name of the institutions, required
:schools: dict, this is more for universities, but it be used for larger divisions in big organizations, optional
:state: string, the state where the institution is, optional
:street: string, the street where the institution is, optional
:updated: ['string', 'datetime', 'date'], a datetime when the entry was updated, optional
:uuid: string, a uuid for the entry, optional
:year: integer, the year the entry was created, optional
:zip: ['integer', 'string'], the zip or postal code of the institution, optional


YAML Example
------------

.. code-block:: yaml

	columbiau:
	  aka:
	    - Columbia University
	    - Columbia
	  city: New York
	  country: USA
	  day: 30
	  departments:
	    apam:
	      aka:
	        - APAM
	      name: Department of Applied Physics and Applied Mathematics
	    chemistry:
	      aka:
	        - Chemistry
	        - Dept. of Chemistry
	      name: Department of Chemistry
	    physics:
	      aka:
	        - Dept. of Physics
	        - Physics
	      name: Department of Physics
	  month: May
	  name: Columbia University
	  schools:
	    seas:
	      aka:
	        - SEAS
	        - Columbia Engineering
	        - Fu Foundation School of Engineering and Applied Science
	      name: School of Engineering and Applied Science
	  state: NY
	  street: 500 W 120th St
	  updated: '2020-05-30'
	  uuid: avacazdraca345rfsvwre
	  year: 2020
	  zip: '10027'
	usouthcarolina:
	  aka:
	    - The University of South Carolina
	  city: Columbia
	  country: USA
	  day: 30
	  departments:
	    apam:
	      aka:
	        - APAM
	      name: Department of Applied Physics and Applied Mathematics
	    chemistry:
	      aka:
	        - Chemistry
	        - Dept. of Chemistry
	      name: Department of Chemistry
	    mechanical engineering:
	      aka:
	        - Mechanical
	        - Dept. of Mechanical
	      name: Department of Mechanical Engineering
	    physics:
	      aka:
	        - Dept. of Physics
	        - Physics
	      name: Department of Physics
	  month: May
	  name: The University of South Carolina
	  schools:
	    cec:
	      aka:
	        - CEC
	        - College of Engineering and Computing
	      name: College of Engineering and Computing
	  state: SC
	  street: 1716 College Street
	  updated: '2020-06-30'
	  uuid: 4E89A0DD-19AE-45CC-BCB4-83A2D84545E3
	  year: 2020
	  zip: '29208'


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "columbiau",
	    "aka": [
	        "Columbia University",
	        "Columbia"
	    ],
	    "city": "New York",
	    "country": "USA",
	    "day": 30,
	    "departments": {
	        "apam": {
	            "aka": [
	                "APAM"
	            ],
	            "name": "Department of Applied Physics and Applied Mathematics"
	        },
	        "chemistry": {
	            "aka": [
	                "Chemistry",
	                "Dept. of Chemistry"
	            ],
	            "name": "Department of Chemistry"
	        },
	        "physics": {
	            "aka": [
	                "Dept. of Physics",
	                "Physics"
	            ],
	            "name": "Department of Physics"
	        }
	    },
	    "month": "May",
	    "name": "Columbia University",
	    "schools": {
	        "seas": {
	            "aka": [
	                "SEAS",
	                "Columbia Engineering",
	                "Fu Foundation School of Engineering and Applied Science"
	            ],
	            "name": "School of Engineering and Applied Science"
	        }
	    },
	    "state": "NY",
	    "street": "500 W 120th St",
	    "updated": "2020-05-30",
	    "uuid": "avacazdraca345rfsvwre",
	    "year": 2020,
	    "zip": "10027"
	}
	{
	    "_id": "usouthcarolina",
	    "aka": [
	        "The University of South Carolina"
	    ],
	    "city": "Columbia",
	    "country": "USA",
	    "day": 30,
	    "departments": {
	        "apam": {
	            "aka": [
	                "APAM"
	            ],
	            "name": "Department of Applied Physics and Applied Mathematics"
	        },
	        "chemistry": {
	            "aka": [
	                "Chemistry",
	                "Dept. of Chemistry"
	            ],
	            "name": "Department of Chemistry"
	        },
	        "mechanical engineering": {
	            "aka": [
	                "Mechanical",
	                "Dept. of Mechanical"
	            ],
	            "name": "Department of Mechanical Engineering"
	        },
	        "physics": {
	            "aka": [
	                "Dept. of Physics",
	                "Physics"
	            ],
	            "name": "Department of Physics"
	        }
	    },
	    "month": "May",
	    "name": "The University of South Carolina",
	    "schools": {
	        "cec": {
	            "aka": [
	                "CEC",
	                "College of Engineering and Computing"
	            ],
	            "name": "College of Engineering and Computing"
	        }
	    },
	    "state": "SC",
	    "street": "1716 College Street",
	    "updated": "2020-06-30",
	    "uuid": "4E89A0DD-19AE-45CC-BCB4-83A2D84545E3",
	    "year": 2020,
	    "zip": "29208"
	}

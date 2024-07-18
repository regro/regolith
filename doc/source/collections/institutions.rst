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
:departments: dict, all the departments and centers andvarious units in the institution, optional
:name: string, the canonical name of the institutions, required
:schools: dict, this is more for universities, but it be used for larger divisions in big organizations, optional
:state: string, the state where the institution is, optional
:street: string, the street where the institution is, optional
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
	  departments:
	    apam:
	      aka:
	        - APAM
	      name: Department of Applied Physicsand Applied Mathematics
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
	  zip: '10027'


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
	    "departments": {
	        "apam": {
	            "aka": [
	                "APAM"
	            ],
	            "name": "Department of Applied Physicsand Applied Mathematics"
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
	    "zip": "10027"
	}

Students
========
This is a collection of student names and metadata. This should probably be private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, short representation, such as this-is-my-name, required
:aka: ['list', 'string'], list of aliases, optional

	:type: string, optional
:email: string, email address, optional
:university_id: string, The university identifier for the student, optional


YAML Example
------------

.. code-block:: yaml

	Human A. Person:
	  aka:
	    - H. A. Person
	  email: haperson@uni.edu
	  university_id: HAP42


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Human A. Person",
	    "aka": [
	        "H. A. Person"
	    ],
	    "email": "haperson@uni.edu",
	    "university_id": "HAP42"
	}

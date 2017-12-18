Assignments
===========
Information about assignments for classes.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, A unique id for the assignment, such a HW01-EMCH-558-2016-S, required
:category: string, such as 'homework' or 'final', required
:courses: string, ids of the courses that have this assignment, required
:file: string, path to assignment file in store, optional
:points: ('integer', 'float'), list of number of points possible for each question. Length is the number of questions, required
:question: string, titles for the questions on this assignment, optional
:solution: string, path to solution file in store, optional


YAML Example
------------

.. code-block:: yaml

	hw01-rx-power:
	  courses:
	    - EMCH-558-2016-S
	    - EMCH-758-2016-S
	  category: homework
	  points:
	    - 1
	    - 2
	    - 3
	  questions:
	    - 1-9
	    - 1-10
	    - 1-12


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "hw01-rx-power",
	    "category": "homework",
	    "courses": [
	        "EMCH-558-2016-S",
	        "EMCH-758-2016-S"
	    ],
	    "points": [
	        1,
	        2,
	        3
	    ],
	    "questions": [
	        "1-9",
	        "1-10",
	        "1-12"
	    ]
	}

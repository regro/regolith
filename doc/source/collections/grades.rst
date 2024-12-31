Grades
======
The grade for a student on an assignment. This information should be private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique id, typically the student-assignment-course, required
:assignment: string, assignment id, required
:course: string, course id, required
:filename: string, path to file in store, optional
:scores: list, the number of points earned on each question, required

	:anyof_type: ['integer', 'float'], optional
:student: string, student id, required


YAML Example
------------

.. code-block:: yaml

	Human A. Person-rx-power-hw02-EMCH-758-2017-S:
	  assignment: 2017-rx-power-hw02
	  course: EMCH-758-2017-S
	  scores:
	    - 1
	    - 1.6
	    - 3
	  student: hap


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Human A. Person-rx-power-hw02-EMCH-758-2017-S",
	    "assignment": "2017-rx-power-hw02",
	    "course": "EMCH-758-2017-S",
	    "scores": [
	        1,
	        1.6,
	        3
	    ],
	    "student": "hap"
	}

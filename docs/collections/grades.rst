Grades
============
The grade for a student on an assignment. This information should be private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, unique id, typically the student-assignment-course
:student: str,  student id
:assignment: str,  assignment id
:course: str, course id
:scores: list of int or float,  the number of points earned on each question
:filename: str,  path to file in store, optional


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


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "Human A. Person-rx-power-hw02-EMCH-758-2017-S",
     "assignment": "2017-rx-power-hw02",
     "course": "EMCH-758-2017-S",
     "scores": [1, 1.6, 3]}

Assignments
============
Information about assignments for classes.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, A unique id for the assignment, such a HW01-EMCH-558-2016-S
:courses: list of str,  ids of the courses that have this assignment
:category: str, such as 'homework' or 'final'
:file: str, path to assignment file in store, optional
:solution: str, path to solution file in store, optional
:question: list of str,  titles for the questions on this assignment,
    optional, defaults to 1-indexed ints if absent.
:points: list of int or float, list of number of points possible for each
    question. Length is the number of questions


YAML Example
------------

.. code-block:: yaml

    hw01-rx-power:
      category: homework
      courses:
        - EMCH-558-2016-S
        - EMCH-758-2016-S
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

    {"_id": "hw01-rx-power",
     "category": "homework",
     "courses": ["EMCH-558-2016-S", "EMCH-758-2016-S"],
     "points": [1, 2, 3],
     "questions": ["1-9", "1-10", "1-12"]}

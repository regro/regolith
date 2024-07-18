Courses
============
This is a collection that describes a course, when it happened, and
who is taking it. This is likely private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, course unique id, such a EMCH-558-2016-S
:department: str, department code, e.g. EMCH
:number: int or str, class number, e.g. 558
:year: int, year taught, e.g. 2016
:season: str,  semester or quarter instructed in, e.g. 'F', 'W', 'S', or 'M'
:students: list of str, names of students enrolled in course
:syllabus: str,  syllabus file name in store, optional
:scale: list of 2-lists of ``[float, str]`` This is a listing of lower bounds (as a faction)
    and the grade that is achieved by obtaining greater than or equal to that value.
:weights: dict of str keys and float values,  mapping from assignment category name
    to fraction of final grade.
:active: bool, whether  or not the course is actively being taught


YAML Example
------------

.. code-block:: yaml

    EMCH-552-2016-F:
      active: false
      season: F
      department: EMCH
      number: 552
      scale:
        -   - 0.875
            - A
        -   - 0.8125
            - B+
        -   - 0.75
            - B
        -   - 0.6875
            - C+
        -   - 0.625
            - C
        -   - 0.5625
            - D+
        -   - 0.5
            - D
        -   - -1.0
            - F
      students:
        - Human A. Person
        - Human B. Person
      syllabus: emch552-2016-f-syllabus.pdf
      weights:
        class-notes: 0.15
        final: 0.3
        homework: 0.35
        midterm: 0.2
      year: 2016



JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "EMCH-552-2016-F",
     "active": false,
     "department": "EMCH",
     "number": 552,
     "scale": [[0.875, "A"],
               [0.8125, "B+"],
               [0.75, "B"],
               [0.6875, "C+"],
               [0.625, "C"],
               [0.5625, "D+"],
               [0.5, "D"],
               [-1.0, "F"]],
     "season": "F",
     "students": ["Human A. Person", "Human B. Person"],
     "syllabus": "emch552-2016-f-syllabus.pdf",
     "weights": {"class-notes": 0.15,
                 "final": 0.3,
                 "homework": 0.35,
                 "midterm": 0.2},
     "year": 2016}

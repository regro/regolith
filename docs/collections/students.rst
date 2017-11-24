Students
============
This is a collection of student names and metadata. This should probably be private.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, short represntation, such as this-is-my-name
:aka: list of str, list of aliases, optional
:email: str, email address, optional
:university_id: str, The university identifier for the student, optional

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

    {"_id": "Human A. Person",
     "aka": ["H. A. Person"],
     "email": "haperson@uni.edu",
     "university_id": "HAP42"}

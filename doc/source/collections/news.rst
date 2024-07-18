News
============
This collection describes the research group news. This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, Unique identifier for the news
:body: str, the main text of the new story
:author: str, Name that should match a person or AKA
:year: int, publication year
:month: str, publication month
:day: int, publication day


YAML Example
------------

.. code-block:: yaml

    56b4eb6d421aa921504ef2a9:
      author: Anthony Scopatz
      body: Dr. Robert Flanagan joined ERGS as a post-doctoral scholar.
      day: 1
      month: February
      year: 2016


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "56b4eb6d421aa921504ef2a9",
     "author": "Anthony Scopatz",
     "body": "Dr. Robert Flanagan joined ERGS as a post-doctoral scholar.",
     "day": 1,
     "month": "February",
     "year": 2016}

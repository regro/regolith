Blog
============
This collection represents blog posts written by the members of the research group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, short represntation, such as this-is-my-title
:title: str,  full human readable title
:original: str, URL of original post, if this is a repost, optional
:author: str, name or AKA of author
:year: int, Publication year
:month: str, Publication month
:day: int, Publication day
:post: str, actual contents of the post


YAML Example
------------

.. code-block:: yaml

    my-vision:
        title: My Vision
        author: Anthony Scopatz
        year: 2015
        month: September
        day: 18
        original: https://scopatz.com/my-vision/
        post: |
            I would like see things move forward. Deep, I know!


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "my-vision",
     "title": "My Vision",
     "author": "Anthony Scopatz",
     "year": 2015,
     "month": "September",
     "day": 18,
     "original": "https://scopatz.com/my-vision/",
     "post": "I would like see things move forward. Deep, I know!"}

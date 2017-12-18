Blog
====
This collection represents blog posts written by the members of the research group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, short represntation, such as this-is-my-title, required
:author: string, name or AKA of author, required
:day: integer, Publication day, required
:month: string, Publication month, required
:original: string, URL of original post, if this is a repost, optional
:post: string, actual contents of the post, required
:title: string, full human readable title, required
:year: integer, Publication year, required


YAML Example
------------

.. code-block:: yaml

	my-vision:
	  year: 2015
	  title: My Vision
	  day: 18
	  post: I would like see things move forward. Deep, I know!
	  author: Anthony Scopatz
	  original: https://scopatz.com/my-vision/
	  month: September


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "my-vision",
	    "author": "Anthony Scopatz",
	    "day": 18,
	    "month": "September",
	    "original": "https://scopatz.com/my-vision/",
	    "post": "I would like see things move forward. Deep, I know!",
	    "title": "My Vision",
	    "year": 2015
	}

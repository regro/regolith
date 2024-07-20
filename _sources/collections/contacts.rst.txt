Contacts
========
a lighter version of people.  Fewer required fields for capturing people who are less tightly coupled

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:aka: list, other names for the person, optional
:date: ['string', 'date'], date when the entry was created in ISO format, optional
:day: integer, day when the entry was created, optional
:department: string, Department at the institution, optional
:email: string, Contact email for the contact, optional
:institution: string, the institution where they are located.  This isrequired for building a COI list of coauthors, butnot in general.  It can be institute id or anythingin the aka or name, optional
:month: ['string', 'integer'], month when the entry was created, optional
:name: string, the person's canonical name, required
:notes: ['list', 'string'], notes about the person, optional
:title: string, how the person is addressed, optional
:updated: ['string', 'datetime', 'date'], most recently updated, optional
:uuid: string, universally unique identifier, optional
:year: integer, year when the entry was created, optional


YAML Example
------------

.. code-block:: yaml

	afriend:
	  aka:
	    - A. B. Friend
	    - AB Friend
	    - Tony Friend
	  day: 15
	  department: physics
	  email: friend@deed.com
	  institution: columbiau
	  month: January
	  name: Anthony B Friend
	  notes:
	    - The guy I meet for coffee sometimes
	  title: Mr.
	  uuid: 76f2a4c7-aa63-4fa3-88b5-396b0c15d368
	  year: 2020


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "afriend",
	    "aka": [
	        "A. B. Friend",
	        "AB Friend",
	        "Tony Friend"
	    ],
	    "day": 15,
	    "department": "physics",
	    "email": "friend@deed.com",
	    "institution": "columbiau",
	    "month": "January",
	    "name": "Anthony B Friend",
	    "notes": [
	        "The guy I meet for coffee sometimes"
	    ],
	    "title": "Mr.",
	    "uuid": "76f2a4c7-aa63-4fa3-88b5-396b0c15d368",
	    "year": 2020
	}

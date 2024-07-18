Contacts
========
a lighter version of people.  Fewer required fieldsfor capturing people who are less tightly coupled

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:aka: list, other names for the person, optional
:department: string, Department at the institution, optional
:email: string, Contact email for the contact, optional
:institution: string, the institution where they are located.  This isrequired for building a COI list of coauthors, butnot in general.  It can be institute id or anythingin the aka or name, optional
:name: string, the person canonical name, required
:notes: ['list', 'string'], notes about the person, optional
:title: string, how the person is addressed, optional


YAML Example
------------

.. code-block:: yaml

	afriend:
	  aka:
	    - A. B. FriendAB FriendTony Friend
	  department: physics
	  email: friend@deed.com
	  institution: columbiau
	  name: Anthony B Friend
	  notes: The guy I meet for coffee sometimes
	  title: Mr.


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "afriend",
	    "aka": [
	        "A. B. FriendAB FriendTony Friend"
	    ],
	    "department": "physics",
	    "email": "friend@deed.com",
	    "institution": "columbiau",
	    "name": "Anthony B Friend",
	    "notes": "The guy I meet for coffee sometimes",
	    "title": "Mr."
	}

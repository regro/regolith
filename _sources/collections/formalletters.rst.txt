Formalletters
=============
Letters with a formal formatting, subject, recipients, enclosures, etc.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ['string', 'integer', 'float'], short representation, such as id_of_the_letter, required
:copy_to: ['list'], List of people who will receive a copy, optional
:date: ['string', 'date'], Letter date.  ISO format YYYY-MM-DD, required
:encls: ['list'], List of enclosures, optional

	:name: string, The name of the sender, optional
	:title: string, The title of the person, Sir, Mr., Major. Ranks can be shortened to codes., optional
	:postfix: string, The post-fix, PhD, (Admiral, retired), whatever, optional
:paras: ['list'], content of the letter in the form of a List of paragraphs, required
:refs: ['list'], List of references, optional
:subject: ['string'], The subject of the letter, optional

	:name: string, The name of the recipient, optional
	:title: string, The title of the person, Sir, Mr., Major. Ranks can be shortened to codes., optional
	:postfix: string, The post-fix, PhD, (Admiral, retired), whatever, optional


YAML Example
------------

.. code-block:: yaml

	first_letter:
	  copy_to:
	    - copied-person1
	    - copied-person2
	  date: '2022-06-05'
	  encls:
	    - encl 1
	    - encl 2
	  from:
	    name: John Doy
	    postfix: Royalty
	    title: Sir
	  paras:
	    - first paragraph made long enough to make sure the wrapping gives the desired
	      result and that it looks nice all around.
	    - para 2
	    - para 3
	  refs:
	    - ref 1
	    - ref 2
	  subject: this letter is about this
	  to:
	    name: Julie Doe
	    postfix: USM
	    title: lc


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "first_letter",
	    "copy_to": [
	        "copied-person1",
	        "copied-person2"
	    ],
	    "date": "2022-06-05",
	    "encls": [
	        "encl 1",
	        "encl 2"
	    ],
	    "from": {
	        "name": "John Doy",
	        "postfix": "Royalty",
	        "title": "Sir"
	    },
	    "paras": [
	        "first paragraph made long enough to make sure the wrapping gives the desired result and that it looks nice all around.",
	        "para 2",
	        "para 3"
	    ],
	    "refs": [
	        "ref 1",
	        "ref 2"
	    ],
	    "subject": "this letter is about this",
	    "to": {
	        "name": "Julie Doe",
	        "postfix": "USM",
	        "title": "lc"
	    }
	}

Reading_Lists
=============
Reading lists consist of doi's or urls of items and a brief synopsis of why they are interesting

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique identifier for the reading list., required
:date: ['date', 'string'], date the list was edited, optional
:day: integer, The day the list was edited, optional
:month: ['integer', 'string'], The month the list was edited, optional
:papers: list, The list of items that are in the list, required

	:type: dict, optional

		:doi: string, the doi of the paper.  If it doesn't have one put 'na', optional
		:text: string, the description of why the item is important or interesting, optional
		:url: string, the url of the item if it has one, optional
:purpose: string, The purpose or target audience for the list, optional
:title: string, The title of the list, required
:year: integer, The day the list was edited, optional


YAML Example
------------

.. code-block:: yaml

	african_swallows:
	  date: '2019-12-01'
	  papers:
	    - doi: 10.1107/97809553602060000935
	      text: Very basic, but brief, intro to african swallows
	  title: A step-by-step pathway towards african swallow understanding.
	getting_started_with_pdf:
	  day: 15
	  month: 12
	  papers:
	    - doi: 10.1107/97809553602060000935
	      text: Very basic, but brief, intro to powder diffraction in general
	    - doi: 10.1039/9781847558237-00464
	      text: Lightest weight overview of PDF analysis around.  Good starting point
	    - text: Download and install PDFgui software and run through the step by step
	        tutorial under the help tab
	      url: http://www.diffpy.org
	  purpose: Beginning reading about PDF
	  title: A step-by-step pathway towards PDF understanding.  It is recommended to read
	    the papers in the order they are listed here.
	  year: 2019


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "african_swallows",
	    "date": "2019-12-01",
	    "papers": [
	        {
	            "doi": "10.1107/97809553602060000935",
	            "text": "Very basic, but brief, intro to african swallows"
	        }
	    ],
	    "title": "A step-by-step pathway towards african swallow understanding."
	}
	{
	    "_id": "getting_started_with_pdf",
	    "day": 15,
	    "month": 12,
	    "papers": [
	        {
	            "doi": "10.1107/97809553602060000935",
	            "text": "Very basic, but brief, intro to powder diffraction in general"
	        },
	        {
	            "doi": "10.1039/9781847558237-00464",
	            "text": "Lightest weight overview of PDF analysis around.  Good starting point"
	        },
	        {
	            "text": "Download and install PDFgui software and run through the step by step tutorial under the help tab",
	            "url": "http://www.diffpy.org"
	        }
	    ],
	    "purpose": "Beginning reading about PDF",
	    "title": "A step-by-step pathway towards PDF understanding.  It is recommended to read the papers in the order they are listed here.",
	    "year": 2019
	}

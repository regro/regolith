Groups
======
Information about the research groupthis is generally public information

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique identifier for submission. This generally includes the author name and part of the title., required
:aka: list, other names for the group, required
:banner: string, name of image file with the group banner, optional
:department: string, Name of host department, required
:email: string, Contact email for the group, required
:institution: string, Name of the host institution, required
:mission_statement: string, Mission statement of the group, optional
:name: string, Name of the group, required
:pi_name: string, The name of the Principle Investigator, required
:projects: string, About line for projects, required
:website: string, URL to group webpage, optional


YAML Example
------------

.. code-block:: yaml

	ergs:
	  aka:
	    - Energy Research Group Something
	    - Scopatz Group
	  department: Mechanical Engineering
	  email: <b>scopatz</b> <i>(AT)</i> <b>cec.sc.edu</b>
	  institution: University of South Carolina
	  mission_statement: We are committed to open and accessible research tools and methods.
	  name: ERGS
	  pi_name: Anthony Scopatz
	  projects: ERGS is involved in a large number of computational projects.
	  website: www.ergs.sc.edu


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "ergs",
	    "aka": [
	        "Energy Research Group Something",
	        "Scopatz Group"
	    ],
	    "department": "Mechanical Engineering",
	    "email": "<b>scopatz</b> <i>(AT)</i> <b>cec.sc.edu</b>",
	    "institution": "University of South Carolina",
	    "mission_statement": "We are committed to open and accessible research tools and methods.",
	    "name": "ERGS",
	    "pi_name": "Anthony Scopatz",
	    "projects": "ERGS is involved in a large number of computational projects.",
	    "website": "www.ergs.sc.edu"
	}

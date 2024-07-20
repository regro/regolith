Abstracts
=========
Abstracts for a conference or workshop. This is generally public information

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique identifier for submission. This generally includes the author name and part of the title., required
:coauthors: string, names of coauthors, optional
:email: string, contact email for the author., required
:firstname: string, first name of the author., required
:institution: string, name of the institution, required
:lastname: string, last name of the author., required
:references: string, HTML string of reference for the abstract itself, optional
:text: string, HTML string of the abstract., required
:timestamp: string, The time when the abstract was submitted., required
:title: string, title of the presentation/paper., required


YAML Example
------------

.. code-block:: yaml

	Mouginot.Model:
	  coauthors: P.P.H. Wilson
	  email: mouginot@wisc.edu
	  firstname: Baptiste
	  institution: University of Wisconsin-Madison
	  lastname: Mouginot
	  references: '[1] B. MOUGINOT, “cyCLASS: CLASS models for Cyclus,”, Figshare, https://dx.doi.org/10.6084/m9.figshare.3468671.v2
	    (2016).'
	  text: The CLASS team has developed high quality predictors based on pre-trained
	    neural network...
	  timestamp: 5/5/2017 13:15:59
	  title: Model Performance Analysis


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "Mouginot.Model",
	    "coauthors": "P.P.H. Wilson",
	    "email": "mouginot@wisc.edu",
	    "firstname": "Baptiste",
	    "institution": "University of Wisconsin-Madison",
	    "lastname": "Mouginot",
	    "references": "[1] B. MOUGINOT, \u201ccyCLASS: CLASS models for Cyclus,\u201d, Figshare, https://dx.doi.org/10.6084/m9.figshare.3468671.v2 (2016).",
	    "text": "The CLASS team has developed high quality predictors based on pre-trained neural network...",
	    "timestamp": "5/5/2017 13:15:59",
	    "title": "Model Performance Analysis"
	}

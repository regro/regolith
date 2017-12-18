Grants
======
This collection represents grants that have been awarded to the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ('string', 'integer', 'float'), short representation, such as this-is-my-name, required
:amount: ('integer', 'float'), value of award, required
:begin_day: integer, start day of the grant, optional
:begin_month: string, start month of the grant, required
:begin_year: integer, start year of the grant, required
:benefit_of_collaboration: string, optional
:call_for_proposals: string, optional
:currency: string, typically '$' or 'USD', optional
:end_day: ('string', 'integer'), end day of the grant, optional
:end_month": string, end month of the grant, optional
:end_year: integer, end year of the grant, required
:funder: string, the agency funding the work, required
:grant_id: string, the identfier for this work, optional
:narrative: string, optional
:program: string, the program the work was funded under, required
:status: string, status of the grant, required
:team: list, information about the team members participating in the grant., required


		:position: string, optional
		:cv: string, optional
		:name: string, optional
		:subaward_amount: ('integer', 'float'), optional
		:institution: string, optional

		:position: string, optional
		:cv: string, optional
		:name: string, optional
		:subaward_amount: ('integer', 'float'), optional
		:institution: string, optional
:title: string, actual title of proposal / grant, required


YAML Example
------------

.. code-block:: yaml

	SymPy-1.1:
	  amount: 3000.0
	  begin_month: May
	  begin_year: 2017
	  team:
	    - name: Anthony Scopatz
	      position: PI
	      institution: University of South Carolina
	    - name: Aaron Meurer
	      position: researcher
	      institution: University of South Carolina
	  call_for_proposals: https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ
	  end_year: 2017
	  end_month: December
	  end_day: 31
	  narrative: https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing
	  title: SymPy 1.1 Release Support
	  funder: NumFOCUS
	  program: Small Development Grants
	  begin_day: 1


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "SymPy-1.1",
	    "amount": 3000.0,
	    "begin_day": 1,
	    "begin_month": "May",
	    "begin_year": 2017,
	    "call_for_proposals": "https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
	    "end_day": 31,
	    "end_month": "December",
	    "end_year": 2017,
	    "funder": "NumFOCUS",
	    "narrative": "https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing",
	    "program": "Small Development Grants",
	    "team": [
	        {
	            "institution": "University of South Carolina",
	            "name": "Anthony Scopatz",
	            "position": "PI"
	        },
	        {
	            "institution": "University of South Carolina",
	            "name": "Aaron Meurer",
	            "position": "researcher"
	        }
	    ],
	    "title": "SymPy 1.1 Release Support"
	}

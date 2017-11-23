Grants
============
This collection represents grants that have been awarded to the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str or number, short represntation, such as this-is-my-name
:title: str, actual title of proposal / grant
:funder: str, the agency funding the work
:program: str, the program the work was funded under
:grant_id: str, optional, the identfier for this work, eg #42024
:call_for_proposals: str,  optional, URL to the call for proposals
:narrative: str, optional, URL of document
:benefit_of_collaboration: str, optional, URL of document
:amount: int or float, value of award
:currency: str, typically '$' or 'USD'
:begin_year: int, start year of the grant
:begin_month: str, start month of the grant
:begin_day: int,  start day of the grant, optional
:end_year: int, end year of the grant
:end_month": str, end month of the grant
:end_day: str, end day of teh grant, optional
:team: list of dicts, information about the team members participating in the grant.
    These dicts have the following form:

    .. code-block:: python

        [{"name": str, # should match a person's name  or AKA
          "position": str,   # PI, Co-PI, Co-I, Researcher, etc.
          "institution": str, # The institution of this investigator
          "subaward_amount", int or float,  # optional
          "cv": str,  # optional, URL of document
          },
          ...
          ]


YAML Example
------------

.. code-block:: yaml


    SymPy-1.1:
      amount: 3000.0
      begin_day: 1
      begin_month: May
      begin_year: 2017
      call_for_proposals: https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ
      end_day: 31
      end_month: December
      end_year: 2017
      funder: NumFOCUS
      narrative: https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing
      program: Small Development Grants
      team:
        - institution: University of South Carolina
          name: Anthony Scopatz
          position: PI
        - institution: University of South Carolina
          name: Aaron Meurer
          position: researcher
      title: SymPy 1.1 Release Support



JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "SymPy-1.1",
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
     "team": [{"institution": "University of South Carolina",
               "name": "Anthony Scopatz",
               "position": "PI"},
              {"institution": "University of South Carolina",
               "name": "Aaron Meurer",
               "position": "researcher"}
            ],
     "title": "SymPy 1.1 Release Support"}

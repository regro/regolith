Proposals
============
This collection represents proposals that have been submitted by the group.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str or number, short represntation, such as this-is-my-name
:title: str, actual title of proposal
:pi: str, principal investigator name
:authors: list of str, other investigator names
:status: str, e.g. 'submitted', 'accepted', 'rejected'
:ammount: int or float, value of award
:currency: str, typically '$' or 'USD'
:durration: int or float, number of years
:year: int, Year that the proposal is due
:month: str, month that the proposal is due
:day: int, day that the proposal is due
:pre: dict,  Information about the pre-proposal, optional.
    This dict has the following form:

    .. code-block:: python

        {"year": int,
         "month": str,
         "day": int,
         "narrative": str, # URL of document
         "benefit_of_collaboration": str, # URL of document
         "cv": list of str, # URL to documents
         }

:full: Information about the pre-proposal, optional
    This dict has the following form:

    .. code-block:: python

        {"narrative": str, # URL of document
         "benefit_of_collaboration": str, # URL of document
         "cv": list of str, # URL to documents
         }


YAML Example
------------

.. code-block:: yaml

    mypropsal:
        title: A very fine proposal indeed
        pi: Anthony Scopatz
        authors:
            - Anthony Scopatz
            - Robert Flanagan
        status: submitted
        ammount: 1000000.0
        currency: USD
        durration: 3
        year: 1999
        month: Aug
        day: 18
        pre:
            year: 1998
            month: Aug
            day: 2
            narrative: http://some.com/pdf
            benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
            cv:
                - http://pdf.com/scopatz-cv
                - http://pdf.com/flanagan-cv
        full:
            narrative: http://some.com/pdf
            benefit_of_collaboration: http://pdf.com/benefit_of_collaboration
            cv:
                - http://pdf.com/scopatz-cv
                - http://pdf.com/flanagan-cv


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "mypropsal",
     "title": "A very fine proposal indeed",
     "pi": "Anthony Scopatz",
     "authors": ["Anthony Scopatz",
                 "Robert Flanagan"],
     "status": "submitted",
     "ammount": 1000000.0,
     "currency": "USD",
     "durration": 3,
     "year": 1999,
     "month": "Aug",
     "day": 18,
     "pre": {"year": 1998,
             "month": "Aug",
             "day": 2,
             "narrative": "http://some.com/pdf"
             "benefit_of_collaboration": "http://pdf.com/benefit_of_collaboration",
             "cv": ["http://pdf.com/scopatz-cv",
                    "http://pdf.com/flanagan-cv"]},
     "full": {"narrative": "http://some.com/pdf"
             "benefit_of_collaboration": "http://pdf.com/benefit_of_collaboration",
             "cv": ["http://pdf.com/scopatz-cv",
                    "http://pdf.com/flanagan-cv"]}
    }


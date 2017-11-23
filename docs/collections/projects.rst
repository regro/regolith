Projects
============
This collection describes the research group projects. This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, Unique project identifier.
:name: str, name of the project.
:description: str, brief project description.
:website: str, URL of the website.
:repo: str, URL of the source code repo, if available, optional.
:logo: str, URL to the project logo, optional.
:other: list of str, other information about the project, optional/
:team: list of dict, People who are/have been woking on this project.
    These dicts have the following structure:

    .. code-block:: python

        [{"name": str, # should match a person's name  or AKA
          "position": str,
          "begin_year": int,
          "begin_month": str, # optional
          "end_year": int, # optional
          "end_month": str,  # optional
          },
          ...
          ]


YAML Example
------------

.. code-block:: yaml

    Cyclus:
      description: Agent-Based Nuclear Fuel Cycle Simulator
      logo: http://fuelcycle.org/_static/big_c.png
      other:
        - Discrete facilities with discrete material transactions
        - Low barrier to entry, rapid payback to adoption
      repo: https://github.com/cyclus/cyclus/
      team:
        - begin_month: June
          begin_year: 2013
          end_month: July
          end_year: 2015
          name: Anthony Scopatz
          position: Project Lead
      website: http://fuelcycle.org/


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "Cyclus",
     "description": "Agent-Based Nuclear Fuel Cycle Simulator",
     "logo": "http://fuelcycle.org/_static/big_c.png",
     "other": ["Discrete facilities with discrete material transactions",
               "Low barrier to entry, rapid payback to adoption"],
     "repo": "https://github.com/cyclus/cyclus/",
     "team": [{"begin_month": "June",
               "begin_year": 2013,
               "end_month": "July",
               "end_year": 2015,
               "name": "Anthony Scopatz",
               "position": "Project Lead"}],
     "website": "http://fuelcycle.org/"}

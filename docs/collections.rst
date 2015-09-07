Collections
============
This page describes recommended - but not required - schema for collections of a given name.

people
-------
This collection describes the members of the research group.  This is normally public data. 

.. code:: python

    {"name": str, # Full, canonical name for the person
     "title": str, # eg Dr., etc.
     "position": str,  # such as professor, graduate student, or scientist
     "aka": [str],  # list of aliases
     "avatar": str,  # URL to avatar
     "bio": str,  # short biographical text
     "education": [{  # list of dictionaries
        "institution": str,
        "location": str,
        "degree": str,
        "begin_year": int,
        "begin_month": str, # optional
        "end_year": int,
        "end_month": str,  # optional
        "gpa": float or str, # optional
        "other": [str], # list of strings of other pieces of information
        },
        ...
        ],
     "employment": [{  # list of dicts
        "organization": str,
        "location": str,
        "position": str,
        "begin_year": int,
        "begin_month": str, # optional
        "end_year": int,
        "end_month": str,  # optional
        "other": [str], # list of strings of other pieces of information
        },
        ...
        ],
     "funding": [{ # list of dictionaries
        "name": str,
        "value": float,
        "currency": str, # optional, defaults to "$"
        "year": int, 
        "month": str, # optional
        "duration": str or int, # optional length of award
        },
        ...
        ],
     "service": [{ # list of dictionaries
        "name": str,
        "description": str, 
        "year": int, 
        "month": str, # optional
        "duration": str or int, # optional length of award
        },
        ...
        ],
     "honors": [{ # list of dictionaries
        "name": str,
        "description": str, 
        "year": int, 
        "month": str, # optional
        },
        ...
        ],
     }

citations
-----------
This collection should contain bibtex equivalent fields.  Additionally, the keys ``"entrytype"`` denotes
things like ``ARTICLE``, and ``"_id"`` denotes the entry identifier.  Furthermore, the ``"author"`` key should
be a list of strings.  See the Python project `BibtexParser <https://bibtexparser.readthedocs.org/>`_ for more
information.


Collections
============
This page describes recommended - but not required - schema for collections of a given 
name.

people
-------
This collection describes the members of the research group.  This is normally public 
data. 

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
        "description": str, # optional
        "year": int, 
        "month": str, # optional
        "duration": str or int, # optional length of service
        },
        ...
        ],
     "honors": [{ # list of dictionaries
        "name": str,
        "description": str, # optional
        "year": int, 
        "month": str, # optional
        },
        ...
        ],
     "teaching": [{ # list of dicts
        "course": str,  # name of the course
        "organization": str,
        "position": str,
        "year": int, 
        "month": str, # optional
        "end_year": int, # optional
        "end_month": str,  # optional
        "description": str, # optional
        "website": str,  # optional URL
        "syllabus": str,  # optional URL
        "video": str,  # optional URL
        "materials": str,  # optional URL
        },
        ...
        ],
     "membership": [{ # list of dicts
        "organization": str,
        "position": str,
        "description": str, # optional
        "begin_year": int,
        "begin_month": str, # optional
        "end_year": int, # optional
        "end_month": str,  # optional
        "website": str,  # optional URL
        },
        ...
        ],
     "skills": [{ # list of dicts
        "name": str,
        "category": str, 
        "level": str
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


projects
---------
This collection describes the research group projects. This is normally public data. 

.. code:: python

    {"name": str,
     "description": str,
     "website": str,
     "repo": str, # src code repo, if available
     "logo": str, # url to logo, optional
     "other": [str], # other information, list of str
     "team": [{  # list of dicts
        "name": str, # should match a person's name  or AKA
        "position": str, 
        "begin_year": int,
        "begin_month": str, # optional
        "end_year": int, # optional
        "end_month": str,  # optional
        },
        ...
        ],
    }

news
---------
This collection describes the research group news. This is normally public data. 

.. code:: python

    {"body": str, 
     "author": str, # name that should match a person or AKA
     "year": int, 
     "month": str,
     "day": int,
     }


jobs
---------
This collection describes the research group jobss. This is normally public data. 


.. code:: python

    {"_id": str or number, #
     "title": str,
     "description": str,
     "open": bool,
     "contact": str,  # contact information for how to apply
     "positions": [str], # list of string positions such as "Graduate Student", "Post-doctoral Scholar", etc
     "background_fields": [str], # previous disciplines, eg. Nucleare Engineering or Computer Science
     "year": int, 
     "month": str,
     "day": int,
     "start_date": str,  # date or ASAP or similar
     "expertise": str,
     "compensation": [str], # list of compensations
     }

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
     "active": bool  # If the person is an active member
     "collab": bool  # If the person is a collaborator
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
This collection describes the research group jobs. This is normally public data.


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

blog
-----------
This collection represents blog posts written by the members of the research group.

.. code:: python

    {"_id": str or number, # short represntation, such as this-is-my-title
     "title": str,  # full human readable title
     "original": str,  # URL of original post, if this is a repost, optional
     "author": str, # name or AKA of author
     "year": int,
     "month": str,
     "day": int,
     "post": str, # actual contents of the post
     }


proposals
-----------
This collection represents proposals that have been submitted by the group.

.. code:: python

    {"_id": str or number, # short represntation, such as this-is-my-name
     "title": str, # actual title of proposal
     "pi": str,  # principal investigator name
     "authors": [str], # other investigator names
     "status": str, # e.g. 'submitted', 'accepted', 'rejected'
     "ammount": int or float, # value of award
     "currency": str, # typically '$' or 'USD'
     "durration": int or float, # number of years
     "year": int,
     "month": str,
     "day": int,
     "pre": { # Information about the pre-proposal, optional
        "year": int,
        "month": str,
        "day": int,
        "narrative": str, # URL of document
        "benefit_of_collaboration": str, # URL of document
        "cv": [str], # URL to documents
        },
     "full": { # Information about the pre-proposal, optional
        "narrative": str, # URL of document
        "benefit_of_collaboration": str, # URL of document
        "cv": [str], # URL to documents
        },
     }


grants
------
This collection represents grants that have been awarded to the group.

.. code:: python

    {"_id": str or number, # short represntation, such as this-is-my-name
     "title": str, # actual title of proposal
     "funder": str, # the agency funding the work
     "program": str, # the program the work was funded under
     "grant_id": str, # optional, the identfier for this work, eg #42024
     "call_for_proposals": str,  # optional, URL to the call for proposals
     "narrative": str, # optional, URL of document
     "benefit_of_collaboration": str, # optional, URL of document
     "amount": int or float, # value of award
     "currency": str, # typically '$' or 'USD'
     "begin_year": int,
     "begin_month": str,
     "begin_day": int,  # optional
     "end_year": int,
     "end_month": str,
     "end_day": str,  # optional
     "team": [{  # list of dicts
        "name": str, # should match a person's name  or AKA
        "position": str,   # PI, Co-PI, Co-I, Researcher, etc.
        "institution": str, # The institution of this investigator
        "subaward_amount", int or float,  # optional
        "cv": str,  # optional, URL of document
        },
        ...
        ],
     }


students
-----------
This is a collection of student names and metadata.

.. code:: python

    {"_id": str, # short represntation, such as this-is-my-name
     "aka": [str],  # list of aliases, optional
     "email": str, # email address, optional
    }


courses
----------
This is a collection that describes a course, when it happened, and
who is taking it.

.. code:: python

    {"_id": str, # course unique id, such a EMCH-558-2016-S
     "department": str, # department code, e.g. EMCH
     "number": int or str,  # class number, e.g. 558
     "year": int,  # year taught, e.g. 2016
     "season": str,  # semester or quarter instructed in, e.g. 'F', 'W', 'S', or 'M'
     "students": [str],  # names of students enrolled in course
     "syllabus": str,  # syllabus file name in store, optional
     "weights": {str: float},  # mapping from assignment category name
                               # to fraction of final grade.
     "active": bool,  # whether  or not the course is actively being taught
    }


assignments
------------
Assignment info.

.. code:: python

    {"_id": str, # unique id, such a HW01-EMCH-558-2016-S
     "courses": [str],  # ids of the courses
     "category": str,  # such as 'homework' or 'final'
     "file": str,  # path to assignment file in store, optional
     "solution": str,  # path to solution file in store, optional
     "question": [str],  # titles for the questions on this assignment,
                         # optional, defaults to 1-indexed ints if absent.
     "points": [int or float],  # list of number of points possible for each
                                # question. Length is the number of questions
    }


grades
-------
The grade for a student on an assignment.

.. code:: python

    {"_id": str, # unique id, typically the student-assignment-course
     "student": str,  # student id
     "assignment": str,  # assignment id
     "course": str, # course id
     "scores": [int or float],  # the number of points earned on each question
     "filename": str,  # path to file in store, optional
    }


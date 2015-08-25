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
     }

citations
-----------
This collection should contain bibtex equivalent fields.  Additionally, the keys ``"entrytype"`` denotes
things like ``ARTICLE``, and ``"_id"`` denotes the entry identifier.  Furthermore, the ``"author"`` key should
be a list of strings.  See the Python project `BibtexParser <https://bibtexparser.readthedocs.org/>`_ for more
information.


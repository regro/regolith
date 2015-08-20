Top-level Configuration Keys
================================
Herein are described the top-level keys in the run control file.

``databases``
===============
This represents the public or private databases that are used to store unstructured data about the group 
and its activities.

.. code-block:: python

    [{  # list of dictionaries in order of precedence
     'name': 'x',  # string identifier for databases name
     'url': 'http://...',  # location of database
     'path': 'path/to/database',  # inside of the resource location
     'public': True | False,  # whether the database is fully public or may contain
                              # sensitive information.
     },
     ...
     ]


``stores``
===============
This is used to represent connection information to document stores, think PDFs, images, etc. 

.. code-block:: python

    [{  # list of dictionaries in order of precedence
     'name': 'x',  # string identifier for store name
     'url': 'http://...',  # location of the store
     'path': 'path/to/store' or None,  # inside of the resource location, optional
     'public': True | False,  # whether the store is fully public or may contain
                              # sensitive information.
     },
     ...
     ]


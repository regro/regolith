Top-level Configuration Keys
================================
Herein are described the top-level keys in the run control file.

``builddir``
=============
The temporary location to build whatever it is needs building.

.. code-block:: python

    'path/to/dir' or None  # string, optional


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


---------------------------------
Keys Usually Set by CLI
---------------------------------
The following keys are normally set by the command line interface. However, you 
can set them in the run control file should you choose to.

``cmd``
=========
The command to run.  

.. code-block:: python

    'rc' | 'add' | ...  # str


``db``
=========
The database to use.  This should coorespond to the name field of one of the ``databases`` entries.

``coll``
=========
The collection name inside of a database to use.  

``document``
================
The document to add, update, etc. Should be in JSON / mongodb format.

``public_only``
==================
Boolean for whether to select only public databases.


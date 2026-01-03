---------------------------------
Top-level Configuration Keys
---------------------------------
Herein are described the top-level keys in the run control file.

``builddir``
=============
The temporary location to build whatever it is needs building.

.. code-block:: python

    'path/to/dir' or None  # string, optional


``mongodbpath``
================
The value to pass into the ``--dbpath`` option to ``mongod``.  Defaults to ``'${builddir}/_dbpath'``
if unspecified.


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
     'local': True | False  # Whether or not git, hg, or mongo are locally hosted/updated or full remote
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

``groupname``
=====================
This is a string of the research group name.


``cname``
============
This is a string of the CNAME value.  This will be put into a file called CNAME in the root
HTML build dir, if it is present.


``deploy``
==========
This is a list of deployment targets to send information to from the build directories.


.. code-block:: python

    [{  # list of dictionaries in order of precedence
     'name': 'x',  # string identifier for store name
     'url': 'http://...',  # location of the store
     'src': 'path/to/src/in/builddir', # what are we copying, eg 'html'(optional, the default)
     'dst': 'path/to/dest/in/deploydir/x' or None,  # inside of the resource location, optional
     },
     ...
     ]


``deploydir``
======================
The temporary location to for all deployment directories.  If not present, this
will default to a ``deploy`` dir inside of the ``builddir``

.. code-block:: python

    'path/to/dir' or None  # string, optional

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


``client``
=================
The MongoDB client to use.  This is almost always set by regolith internally.

``db``
=========
The database to use.  This should correspond to the name field of one of the ``databases`` entries.

``coll``
=========
The collection name inside of a database to use.

``documents``
================
List of documents to add, update, etc. Should be in JSON / mongodb format.

``public_only``
==================
Boolean for whether to select only public databases.


``filename``
==============
String that is a path to a file to operate on.

``debug``
================
Boolean for whether to run in debug mode or not.

``blacklist``
===============
List of files to not load when loading databases. If not provided, blacklists
``['.travis.yml', '.travis.yaml']``

``schemas``
===========
Dict of dicts which overrides the schema for a key in a collection.

For example:

.. code-block:: python

    schema = {'people': {'name': {'anyof_type': ['string', 'number']}}}

would allow the names of people to also be
`numbers <https://youtu.be/nW-bFGzNMXw?t=42s>`_.

See the collections for a complete list of the schemas.

``static_source``
=================
File path to the static source for ``regolith build html``. If none provided it defaults to "templates"

This is useful for local website builds where the ``regolithrc.json`` may be in another folder.


------------------
User Configuration
------------------
Users can also provide information available to all databases via a local user
configuration file.
The file must be stored in ``'~/.config/regolith/user.json`` and can have
keys similar to ``regolithrc.json``.
Note that these keys are applied before the ``regolithrc.json`` so if there
are conflicting keys the user keys are overridden.
These keys could be used for storing information for emailing, git remotes,
and other configuration.

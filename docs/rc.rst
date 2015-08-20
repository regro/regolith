Top-level Configuration Keys
================================
Herein are described the top-level keys in the run control file.

``datasets``
===============

.. code-block:: python

    [{  # list of dictionaries in order of precedence
     'name': 'x',  # string identifier for dataset name
     'url': 'http://...',  # location of dataset
     'path': 'path/to/dataset',  # in the resource location
     'public': True | False,  # whether the dataset is fully public or may contain
                              # sensitive information.
     },
     ...
     ]

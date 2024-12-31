ingest
======

.. code-block:: bash

	usage: regolith ingest [-h] [--coll COLL] db filename

	positional arguments:
	  db           database name
	  filename     file to ingest. Currently valid formats are: ['.bib']

	options:
	  -h, --help   show this help message and exit
	  --coll COLL  collection name, if this is not given it is inferred from the
	               file type or file name.

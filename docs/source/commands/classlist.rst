classlist
=========

.. code-block:: bash

	usage: regolith classlist [-h] [-f FORMAT] [-d] [--db DB]
	                          op filename course_id

	positional arguments:
	  op                    operation to perform, such as "add" or "replace".
	  filename              file to read class information from.
	  course_id             course identifier whose registry should be updated

	options:
	  -h, --help            show this help message and exit
	  -f FORMAT, --format FORMAT
	                        file / school format to read information from. Current
	                        values are "json" and "usc". Determined from extension
	                        if not available.
	  -d, --dry-run         only does a dry run and reports results
	  --db DB               database name

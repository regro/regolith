validate
========

.. code-block:: bash

	usage: regolith validate [-h] [--collection COLLECTION]

	options:
	  -h, --help            show this help message and exit
	  --collection COLLECTION
	                        If provided only validate that collection

Misc
----

This can also be added as a git hook by adding the following to
``.git/hooks/pre-commit``

.. code-block:: sh

    #!/bin/sh
    regolith validate

This can be enabled with ``chmod +x .git/hooks/pre-commit``

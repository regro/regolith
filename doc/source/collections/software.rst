Software
========
Information about software, such as active, grants, etc.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, package id, required
:active: boolean, the status whether the package is actively maintained or not., required
:grants: list, grant(s) that supported package development/maintenance, required
:groups: list, research group(s) that develop the package., required
:url: string, url to the package on GitHub or GitLab, etc., required


YAML Example
------------

.. code-block:: yaml

	unique-package-id:
	  active: true
	  grants:
	    - dmref15
	    - SymPy-1.1
	  groups:
	    - ergs
	  url: https://github.com/diffpy/diffpy.utils


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "unique-package-id",
	    "active": true,
	    "grants": [
	        "dmref15",
	        "SymPy-1.1"
	    ],
	    "groups": [
	        "ergs"
	    ],
	    "url": "https://github.com/diffpy/diffpy.utils"
	}

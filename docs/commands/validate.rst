.. _regolith_validate:

******************************************************
``validate``
******************************************************
Validate the combined database against the existing schemas.


Command
-------

.. code-block:: sh

   regolith validate

Misc
----

This can also be added as a git hook by adding the following to
``.git/hooks/pre-commit``

.. code-block:: sh

    #!/bin/sh
    regolith validate

This can be enabled with ``chmod +x .git/hooks/pre-commit``
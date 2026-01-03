Broker
=========

Storing files with the broker
-----------------------------

Sharing figures (and other files) among various group members can be
difficult, as everyone has slightly different file systems.
Regolith has a system to help with this by providing file storage which can
be addressed to various documents in the database. In order to do so, the user
must clone the regolith-storage github directory into their dbs folder, and run
python in a terminal in that (regolith-storage) directory with their
regolith_env conda environment activated. The user must also have push rights to the
regolith-storage git directory, and an SSH connection established.

Loading the broker
******************

To load the broker you need a ``regolithrc.json`` file. This file should
be present in the regolith-storage directory that the user has cloned. The following
block of code should be run in the user's python terminal, in the cloned storage
directory, with the regolith_env conda environment activated. If you intend to
add a file to the heap, do not put the file in the cloned directory before loading the
database as follows.

.. code-block:: python

    from regolith.broker import Broker
    db = Broker.from_rc()

Inserting files into the store
******************************

To insert documents into the broker you can use the ``add_file`` interface.
Due to the fact that the metadata is utilizing a local url and filesystem client,
the user must add, commit, push to origin and PR the effected local databases after
the addition of the file edits their metadata. See below for an example of how to
both create and store a file in the regro document of the projects collection.

Note: Now is the time to take files to be added and paste them into the cloned storage
directory. Do not paste them into the _build folder, but rather the base directory.

.. code-block:: python

    import matplotlib.pyplot as plt

    plt.plot(range(10), range(10))
    plt.savefig('hello_world.png')
    doc = db['projects']['regro']
    db.add_file(doc, 'hw_file', 'hello_world.png')

This will:

    1. copy the file to the store
    2. push the store to the remote repository
    3. add the file to the ``files`` list in the document
    4. save the document to the database
    5. push it to the remote repository

Retrieving files from the store
*******************************

To retrieve files from the store you can use the ``get_file_path`` interface.
Importantly, this will only retrieve the path to the file.

.. code-block:: python

    from regolith.broker import Broker

    db = Broker.from_rc()
    doc = db['projects']['regro']
    path = db.get_file_path(doc, 'hw_file')

This can be used inside tex documents via the ``FigureBuilder`` class/CLI. In order to do so,
the user must have latex installed on their local machine.

Here is an example tex document

.. code-block:: tex

    \documentclass[prb,twocolumn,showpacs,amsmath,amssymb,floatfix]{revtex4-1}
    \usepackage{graphicx}
    \begin{document}
    \title{My paper}
    \author{CJ}
    \affiliation{Department of Applied Physics
    and Applied Mathematics, Columbia University, New York, NY 10027}

    \includegraphics{ {{-get_file_path(db['projects']['regro'], 'hw_file').replace('\\', '/')-}} }
    \end{document}

After running ``regolith build figure`` in the directory
``{{-get_file_path(db['projects']['regro'], 'hw_file').replace('\\', '/')-}}`` will be replaced with
the path to the file in the store.
This way the figure can be accessed across machines in a uniform way.

Note that this isn't limited to figures, any file can be stored in the store,
so if there were boilerplate or short chunks which could be re-used then
they could be stored centrally and retrieved as needed.

Also note that we could have also used the builder to replace other pieces of
the document, eg ``\author{ {{-db['people']['cwright']['name']-}} }`` would
have been replaced with the full name of the author.

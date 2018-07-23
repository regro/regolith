Broker
=========

Storing files with the broker
-----------------------------

Sharing figures (and other files) among various group members can be
difficult, as everyone has slightly different file systems.
Regolith has a system to help with this by providing file storage which can
be addressed to various documents in the database.

Loading the broker
******************

To load the broker you need a ``regolithrc.json`` file.
With that you can use either the class based or function interface

.. code-block:: python

    from regolith.broker import load_db, Broker
    db = load_db('/path/to/regolithrc.json')
    # or
    db = Broker.from_rc('/path/to/regolithrc.json')

Inserting files into the store
******************************

To insert documents into the broker you can use the ``add_file`` interface

.. code-block:: python

    import matplotlib.pyplot as plt
    from regolith.broker import Broker

    db = Broker.from_rc()
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

To retrive files from the store you can use the ``get_file`` interface

.. code-block:: python

    from regolith.broker import Broker

    db = Broker.from_rc()
    doc = db['projects']['regro']
    path = db.get_file(doc, 'hw_file')

This can be used inside tex documents via the ``FigureBuilder`` class/CLI

Here is an example tex document

.. code-block:: tex

    \documentclass[prb,twocolumn,showpacs,amsmath,amssymb,floatfix]{revtex4-1}
    \usepackage{graphicx}
    \begin{document}
    \title{My paper}
    \author{CJ}
    \affiliation{Department of Applied Physics
    and Applied Mathematics, Columbia University, New York, NY 10027}

    \includegraphics{ {{-get_file(db['projects']['regro'], 'hw_file')-}} }
    \end{document}

After running ``regolith build figure`` in the directory
``{{-get_file(db['projects']['regro'], 'hw_file')-}}`` will be replaced with
the path to the file in the store.
This way the figure can be accessed across machines in a uniform way.

Note that this isn't limited to figures, any file can be stored in the store,
so if there were boilerplate or short chuncks which could be re-used then
they could be stored centraly and retrieved as needed.

Also note that we could have also used the builder to replace other pieces of
the document, eg ``\author{ {{-db['people']['cwright']['name']-}} }`` would
have been replaced with the full name of the auther.


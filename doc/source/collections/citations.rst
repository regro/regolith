Citations
============
This collection should contain bibtex equivalent fields.  Additionally,
the keys ``"entrytype"`` denotes things like ``ARTICLE``, and ``"_id"`` denotes
the entry identifier.  Furthermore, the ``"author"`` key should be a list of
strings.  See the Python project `BibtexParser <https://bibtexparser.readthedocs.org/>`_
for more information.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, unique identifier for the citation.

Other keys in this schema are the same as bibtex citations/


YAML Example
------------

.. code-block:: yaml

    meurer2016sympy:
      author:
        - Meurer, Aaron
        - Smith, Christopher P
        - Paprocki, Mateusz
        - "{\\v{C}}ert{\\'\\i}k, Ond{\\v{r}}ej"
        - Rocklin, Matthew
        - Kumar, AMiT
        - Ivanov, Sergiu
        - Moore, Jason K
        - Singh, Sartaj
        - Rathnayake, Thilina
        - Sean Vig
        - Brian E Granger
        - Richard P Muller
        - Francesco Bonazzi
        - Harsh Gupta
        - Shivam Vats
        - Fredrik Johansson
        - Fabian Pedregosa
        - Matthew J Curry
        - Ashutosh Saboo
        - Isuru Fernando
        - Sumith Kulal
        - Robert Cimrman
        - Anthony Scopatz
      entrytype: article
      journal: PeerJ Computer Science
      month: Jan
      pages: e103
      publisher: PeerJ Inc. San Francisco, USA
      title: 'SymPy: Symbolic computing in Python'
      volume: '4'
      year: '2017'



JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "meurer2016sympy",
     "author": ["Meurer, Aaron",
                "Smith, Christopher P",
                "Paprocki, Mateusz",
                "{\\v{C}}ert{\\'\\i}k, Ond{\\v{r}}ej",
                "Rocklin, Matthew",
                "Kumar, AMiT",
                "Ivanov, Sergiu",
                "Moore, Jason K",
                "Singh, Sartaj",
                "Rathnayake, Thilina",
                "Sean Vig",
                "Brian E Granger",
                "Richard P Muller",
                "Francesco Bonazzi",
                "Harsh Gupta",
                "Shivam Vats",
                "Fredrik Johansson",
                "Fabian Pedregosa",
                "Matthew J Curry",
                "Ashutosh Saboo",
                "Isuru Fernando",
                "Sumith Kulal",
                "Robert Cimrman",
                "Anthony Scopatz"],
     "entrytype": "article",
     "journal": "PeerJ Computer Science",
     "month": "Jan",
     "pages": "e103",
     "publisher": "PeerJ Inc. San Francisco, USA",
     "title": "SymPy: Symbolic computing in Python",
     "volume": "4",
     "year": "2017"}

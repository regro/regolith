Abstracts
============
Abstracts for a conference or workshop. This is generally public information

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, Unique identifier for submission. This generally includes the author name and
    part of the title.
:title: str, title of the presentation/paper.
:firstname: str, first name of the author.
:lastname: str, last name of the author.
:coauthors: str, names of coauthors, optional
:email: str, contact email for the author.
:institution: str, name of the inistitution
:references: str, HTML string of reference for the abstract itself, optional
:text: str, HTML string of the abstract.
:timestamp: The time when the abstract was submitted.


YAML Example
------------

.. code-block:: yaml

    Mouginot.Model:
      title: Model Performance Analysis
      firstname: Baptiste
      lastname: Mouginot
      coauthors: P.P.H. Wilson
      email: mouginot@wisc.edu
      institution: University of Wisconsin-Madison
      references: "[1] B. MOUGINOT, “CyCLASS: CLASS models for Cyclus,”, Figshare, https://dx.doi.org/10.6084/m9.figshare.3468671.v2\
        \ (2016).\n[2] B. Mouginot, P.P.H. Wilson, R.W. Carlsen, “Impact of Isotope Fidelity\
        \ on Fuel Cycle Calculations”, ANS Winter Conference, Las Vegas, (November 2016)\n\
        [3] B. Leniau, B. Mouginot, N. Thiollière, X. Doligez, A. Bidaud, F. Courtin,\
        \ M. Ernoult and S. David, “A neural network approach for burn-up calculation\
        \ and its application to the dynamic fuel cycle code CLASS,” Annals of Nuclear\
        \ Energy , 81 , 125 – 133 (2015).\n[4] B. Leniau, F. Courtin, B. Mouginot, N.\
        \ Thiollière, X. Doligez, A. Bidaud, “Generation of SFR Physics Models for the\
        \ Nuclear Fuel Cycle Code CLASS” PHYSOR 2016\n"
      text: "The CLASS team has developed high quality predictors based on pre-trained\
        \ neural networks, allowing the estimation the evolution different neutronic parameters,\
        \ such as neutron multiplication factor or macroscopic cross sections, along the\
        \ irradiation of the fuel. This allows building various fuel fabrication and depletion\
        \ models for fuel cycle simulators. The cyCLASS package [1]  has been developed\
        \ to allow the use of CLASS  fabrication and cross section prediction models inside\
        \ Cyclus. cyCLASS provides a reactor facility and a fuel fabrication facility,\
        \ which are able to use any CLASS models to provide/request fuel to the entire\
        \ Cyclus ecosystem. Using cyCLASS, it has been possible to perform fuel cycle\
        \ simulations comparing different levels of archetypes fidelity[2].\n\nThis work\
        \ focuses on the analysis of the performance of some high fidelity models developed\
        \ from [3,4], extending the isotopic validity space from uranium and plutonium\
        \ to the most common transuranic elements for Light Water Reactors (LWR) and Sodium\
        \ Fast Reactors (SFR). Those extended models were required to study a transition\
        \ scenario from the actual US nuclear fleet to a SFR and LWR fleet reprocessing\
        \ the most commun transuranic elements (see “Recipe vs Model” presentation from\
        \ the same author). The present work aims to evaluate the following for each of\
        \ the models:\nthe performance relative to the training sample density,\nthe precision\
        \ topography inside and outside of the validity space,\nthe performance of the\
        \ burnup calculation for the cross section predictors.\nAs a complete set of real\
        \ data is not available to benchmark such models, their relative performances\
        \ will be evaluated with regards to the depletion tool used to train them.\n"
      timestamp: 5/5/2017 13:15:59


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "Mouginot.Model",
     "coauthors": "P.P.H. Wilson",
     "email": "mouginot@wisc.edu",
     "firstname": "Baptiste",
     "institution": "University of Wisconsin-Madison",
     "lastname": "Mouginot",
     "references": "[1] B. MOUGINOT, \u201ccyCLASS: CLASS models for Cyclus,\u201d, Figshare, https://dx.doi.org/10.6084/m9.figshare.3468671.v2 (2016).",
     "text": "The CLASS team has developed high quality predictors based on pre-trained neural network...",
     "timestamp": "5/5/2017 13:15:59",
     "title": "Model Performance Analysis"}

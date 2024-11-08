Beamplan
========
Information about the experiment plan for the beamtime.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique identifier for the experiment plan. It should have a format '{year:2d}{month:2d}{people_id:s}_{plan_name:s}', required
:beamtime: string, The id for the beamtime. Check the Airtable., required
:begin_date: ['string', 'datetime', 'date'], The begin date of the beam time., required
:devices: list, The dictionary of devices used in the measurement e. g. , required

	:type: string, optional
:end_date: ['string', 'datetime', 'date'], The end date of the beam time., required
:exp_plan: list, Steps to carry out the experiments at BNL. Need details, required

	:type: string, optional
:holder: string, Sample holder used during the measurement, e. g. 3 mm OD tubes holder., required
:measurement: string, What data to be measured, e. g. PDF, XRD, SAXS. This will determine the setup., required
:notes: ['list', 'string'], Notes of the plan, e. g. the preferred time., optional

	:type: string, optional
:objective: string, What to study in the experiments. What goal to achieve., required
:pipeline: string, The analysis pipeline for the experiment. If no new pipeline is needed, use 'usual'., required
:prep_plan: list, Steps to prepare the samples. Do NOT need details., required

	:type: string, optional
:project: string, The id for the project which the plan belongs to. It should be on airtable., required
:project_lead: string, The id for person who put out this plan. It should be inside the people.yml., required
:samples: list, The list of samples to be measured., required

	:type: string, optional
:scanplan: list, The scanplan for the experiment, e. g. tseries, Tramp, ct., required

	:type: string, optional
:ship_plan: list, Steps to carry the samples from the producer to the BNL. Do NOT need details., required

	:type: string, optional
:time: integer, The total time of executing the exp_plan. Unit: min., required
:todo: list, The TODO list before the beamtime., required

	:type: string, optional


YAML Example
------------

.. code-block:: yaml

	test:
	  beamtime: 2020-1-XPD
	  begin_date: '2020-01-01'
	  devices:
	    - cryostream
	  end_date: '2020-01-02'
	  exp_plan:
	    - load samples on the holder
	    - scan the holder to locate the samples
	    - take room temperature measurement of sample and the substrate
	    - ramp down temperature to 100K
	    - ramp up, measure PDF at temperature 100K ~ 300K, 10K stepsize, 1 min exposure
	  holder: film holder (1 cm * 1 cm * 1 mm)
	  measurement: Tramp
	  objective: temperature ramping PDF of one WO3 film (100, 300K, 10K)
	  pipeline: usual
	  prep_plan:
	    - films will be made by kriti
	  project: 20ks_wo3
	  project_lead: kseth
	  samples:
	    - WO3 film
	    - glass substrate
	  scanplan:
	    - Scanplan(bt, Tramp, 30, 80, 500, 10)
	  ship_plan:
	    - seal and ship to CU
	    - carry to the beamline
	  time: 190
	  todo:
	    - todo something


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "test",
	    "beamtime": "2020-1-XPD",
	    "begin_date": "2020-01-01",
	    "devices": [
	        "cryostream"
	    ],
	    "end_date": "2020-01-02",
	    "exp_plan": [
	        "load samples on the holder",
	        "scan the holder to locate the samples",
	        "take room temperature measurement of sample and the substrate",
	        "ramp down temperature to 100K",
	        "ramp up, measure PDF at temperature 100K ~ 300K, 10K stepsize, 1 min exposure"
	    ],
	    "holder": "film holder (1 cm * 1 cm * 1 mm)",
	    "measurement": "Tramp",
	    "objective": "temperature ramping PDF of one WO3 film (100, 300K, 10K)",
	    "pipeline": "usual",
	    "prep_plan": [
	        "films will be made by kriti"
	    ],
	    "project": "20ks_wo3",
	    "project_lead": "kseth",
	    "samples": [
	        "WO3 film",
	        "glass substrate"
	    ],
	    "scanplan": [
	        "Scanplan(bt, Tramp, 30, 80, 500, 10)"
	    ],
	    "ship_plan": [
	        "seal and ship to CU",
	        "carry to the beamline"
	    ],
	    "time": 190,
	    "todo": [
	        "todo something"
	    ]
	}

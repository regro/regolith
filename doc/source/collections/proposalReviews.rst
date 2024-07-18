Proposalreviews
===============
This collection contains reviews of funding proposals

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: ('string', 'integer', 'float'), ID, e.g. 1906_doe_example, required
:adequacy_of_resources: list, Are the resources of the PI adequate, required
:agency: string, currently nsf or doe, optional

	Allowed values: 
		* nsf
		* doe
:competency_of_team: list, Is the team competent, required
:doe_appropriateness_of_approach: list, Appropriateness of Research. only used if agency is doe., optional
:doe_reasonableness_of_budget: list, Reasonableness of budget. only used if agency is doe., optional
:doe_relevance_to_program_mission: list, Relevance to program mission. only used if agency is doe., optional
:does_how: list, How will the research be done, required
:does_what: string, What will the team do, required
:freewrite: list, Anything and this will appear in the built documentright before the summary.  This section often used for extra review criteria for the particular proposal, optional
:goals: list, What are the main goals of the proposed research, required
:importance: list, The importance of the Research, required
:institution: string, The institution of the lead PI, required
:month: ['string', 'integer'], The month the review was submitted, required
:names: ['list', 'string'], The names of the PIs, required
:nsf_broader_impacts: list, The broader impacts of the research.  Only used if agency is nsf, optional
:nsf_create_original_transformative: list, Answer to the question how the work is creative, original or transformative.  Only used if agency is nsf, optional
:nsf_plan_good: list, Is the plan good? Only used if agency is nsf, optional
:nsf_pot_to_Advance_knowledge: list, Answer to the question how the work will advanceknowledge.  Only used if agency is nsf, optional
:nsf_pot_to_benefit_society: list, Answer to the question how the work has the potentialto benefit society.  Only used if agency is nsf, optional
:requester: string, Name of the program officer who requested the review, required
:reviewer: string, short name of the reviewer.  Will be used in the filename of the resulting text file, required
:status: string, the status of the review, optional

	Allowed values: 
		* invited
		* accepted
		* declined
		* downloaded
		* inprogress
		* submitted
:summary: string, Summary statement, required
:title: string, The title of the proposal, required
:year: integer, The year the review was submitted, required


YAML Example
------------

.. code-block:: yaml

	1906doeExample:
	  adequacy_of_resources:
	    - The resources available to the PI seem adequate
	  agency: doe
	  competency_of_team:
	    - super competent!
	  doe_appropriateness_of_approach:
	    - The proposed approach is highly innovative
	  doe_reasonableness_of_budget:
	    - They could do it with half the money
	  doe_relevance_to_program_mission:
	    - super relevant
	  does_how:
	    - they will find the cause of Malaria
	    - when they find it they will determine a cure
	  does_what: Find a cure for Malaria
	  freewrite:
	    - I can put extra things here, such as special instructions from the
	    - program officer
	  goals:
	    - The goals of the proposal are to put together a team to find a curefor Malaria,
	      and then to find it
	  importance:
	    - save lives
	    - lift people from poverty
	  institution: columbiau
	  month: May
	  names:
	    - B. Cause
	    - A.N. Effect
	  nsf_broader_impacts: []
	  nsf_create_original_transformative: []
	  nsf_plan_good: []
	  nsf_pot_to_Advance_knowledge: []
	  nsf_pot_to_benefit_society: []
	  requester: Lane Wilson
	  reviewer: sbillinge
	  status: submitted
	  summary: dynamite proposal
	  title: A stunning new way to cure Malaria
	  year: 2019
	1906nsfExample:
	  adequacy_of_resources:
	    - The resources available to the PI seem adequate
	  agency: nsf
	  competency_of_team:
	    - super competent!
	  doe_appropriateness_of_approach: []
	  doe_reasonableness_of_budget: []
	  doe_relevance_to_program_mission: []
	  does_how:
	    - they will find the cause of Poverty
	    - when they find it they will determine a cure
	  does_what: Find a cure for Poverty
	  freewrite:
	    - I can put extra things here, such as special instructions from the
	    - program officer
	  goals:
	    - The goals of the proposal are to put together a team to find a curefor Poverty,
	      and then to find it
	  importance:
	    - save lives
	    - lift people from poverty
	  institution: upenn
	  month: May
	  names:
	    - A Genius
	  nsf_broader_impacts:
	    - Poor people will be made unpoor
	  nsf_create_original_transformative:
	    - transformative because lives will be transformed
	  nsf_plan_good:
	    - I don't see any issues with the plan
	    - it should be very straightforward
	  nsf_pot_to_Advance_knowledge:
	    - This won't advance knowledge at all
	  nsf_pot_to_benefit_society:
	    - Society will benefit by poor people being made unpoor if they want to be
	  requester: Tessemer Guebre
	  reviewer: sbillinge
	  status: invited,accepted,declined,downloaded,inprogress,submitted
	  summary: dynamite proposal
	  title: A stunning new way to cure Poverty
	  year: 2019


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "1906doeExample",
	    "adequacy_of_resources": [
	        "The resources available to the PI seem adequate"
	    ],
	    "agency": "doe",
	    "competency_of_team": [
	        "super competent!"
	    ],
	    "doe_appropriateness_of_approach": [
	        "The proposed approach is highly innovative"
	    ],
	    "doe_reasonableness_of_budget": [
	        "They could do it with half the money"
	    ],
	    "doe_relevance_to_program_mission": [
	        "super relevant"
	    ],
	    "does_how": [
	        "they will find the cause of Malaria",
	        "when they find it they will determine a cure"
	    ],
	    "does_what": "Find a cure for Malaria",
	    "freewrite": [
	        "I can put extra things here, such as special instructions from the",
	        "program officer"
	    ],
	    "goals": [
	        "The goals of the proposal are to put together a team to find a curefor Malaria, and then to find it"
	    ],
	    "importance": [
	        "save lives",
	        "lift people from poverty"
	    ],
	    "institution": "columbiau",
	    "month": "May",
	    "names": [
	        "B. Cause",
	        "A.N. Effect"
	    ],
	    "nsf_broader_impacts": [],
	    "nsf_create_original_transformative": [],
	    "nsf_plan_good": [],
	    "nsf_pot_to_Advance_knowledge": [],
	    "nsf_pot_to_benefit_society": [],
	    "requester": "Lane Wilson",
	    "reviewer": "sbillinge",
	    "status": "submitted",
	    "summary": "dynamite proposal",
	    "title": "A stunning new way to cure Malaria",
	    "year": 2019
	}
	{
	    "_id": "1906nsfExample",
	    "adequacy_of_resources": [
	        "The resources available to the PI seem adequate"
	    ],
	    "agency": "nsf",
	    "competency_of_team": [
	        "super competent!"
	    ],
	    "doe_appropriateness_of_approach": [],
	    "doe_reasonableness_of_budget": [],
	    "doe_relevance_to_program_mission": [],
	    "does_how": [
	        "they will find the cause of Poverty",
	        "when they find it they will determine a cure"
	    ],
	    "does_what": "Find a cure for Poverty",
	    "freewrite": [
	        "I can put extra things here, such as special instructions from the",
	        "program officer"
	    ],
	    "goals": [
	        "The goals of the proposal are to put together a team to find a curefor Poverty, and then to find it"
	    ],
	    "importance": [
	        "save lives",
	        "lift people from poverty"
	    ],
	    "institution": "upenn",
	    "month": "May",
	    "names": [
	        "A Genius"
	    ],
	    "nsf_broader_impacts": [
	        "Poor people will be made unpoor"
	    ],
	    "nsf_create_original_transformative": [
	        "transformative because lives will be transformed"
	    ],
	    "nsf_plan_good": [
	        "I don't see any issues with the plan",
	        "it should be very straightforward"
	    ],
	    "nsf_pot_to_Advance_knowledge": [
	        "This won't advance knowledge at all"
	    ],
	    "nsf_pot_to_benefit_society": [
	        "Society will benefit by poor people being made unpoor if they want to be"
	    ],
	    "requester": "Tessemer Guebre",
	    "reviewer": "sbillinge",
	    "status": "invited,accepted,declined,downloaded,inprogress,submitted",
	    "summary": "dynamite proposal",
	    "title": "A stunning new way to cure Poverty",
	    "year": 2019
	}

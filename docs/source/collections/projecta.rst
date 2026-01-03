Projecta
========
This collection describes a single deliverable of a larger project.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, Unique projectum identifier, required
:begin_date: ['string', 'date'], projectum start date, yyyy-mm-dd, optional
:collaborators: list, list of collaborators ids. These are non-group members. These will be dereferenced from the contacts collection., optional
:deliverable: dict, outline of the deliverable for this projectum, required

	:audience: list, the target audience for this deliverable, optional
	:due_date: ['date', 'string'], due date of deliverable, yyyy-mm-dd, optional
	:success_def: string, definition of a successful deliverable, optional
	:scope: list, a list of items that define the scope of the deliverable.If this is a software release it might be a list of Use Cases that will be satisfied.If it is a paper it defines what will, and what won't, be described in the paper., optional
	:platform: string, description of how and where the audience will access the deliverable.e.g. Journal if it is a paper. For software releases, this may be the computer operating systems that will be supported, or if it will be a web service, etc., optional
	:roll_out: list, steps that the audience will take to access and interact with the deliverable, not needed for paper submissions, optional
	:notes: list, any notes about the deliverable that we want to keep track of, optional
	:status: string, status of the deliverable. Allowed values are {', '.join(PROJECTUM_STATI)}, optional

		Allowed values:
			* proposed
			* converged
			* started
			* backburner
			* paused
			* cancelled
			* finished
			* all
	:type: string, type of deliverable, optional
:description: string, explanation of projectum, optional
:end_date: ['date', 'string'], projectum end date, yyyy-mm-dd., optional
:grants: ['string', 'list'], grant id funding the project, optional
:group_members: list, list of group member id's working on this project,These will be dereferenced from the people collection., optional
:kickoff: dict, details the projectum kickoff meeting, optional

	:date: ['date', 'string'], kickoff meeting date, yyyy-mm-dd., optional
	:due_date: ['date', 'string'], kickoff meeting by date, yyyy-mm-dd., optional
	:end_date: ['date', 'string'], date when the kickoff was done, optional
	:name: string, name of meeting, optional
	:objective: string, goal of the meeting, optional
	:audience: list, list of people attending the meeting.Normally this list is group_members, collaborators, and pi, or some subset of these. if people are invited who are not alreadyin these groups their names or id's can be added explicitly to the list, optional
	:notes: list, any notes about the kickoff, optional
	:status: string, status of the kickoff. Allowed values are {', '.join(PROJECTUM_STATI)}, optional

		Allowed values:
			* proposed
			* converged
			* started
			* backburner
			* paused
			* cancelled
			* finished
			* all
	:type: string, type of kickoff deliverable. In general will be 'meeting'Allowed values are {', '.join(MILESTONE_TYPES)}, optional

		Allowed values:
			* mergedpr
			* meeting
			* other
			* paper
			* release
			* email
			* handin
			* purchase
			* approval
			* presentation
			* report
			* submission
			* decision
			* demo
			* skel
:lead: string, the id of the lead student or person for the projectum. Person details will be dereferenced from the people collection., required
:log_url: string, link to an online document (e.g., Google doc) that is a log of notes and meeting minutes for the projectum, optional
:milestones: list, smaller deliverables done by a certain date a series of milestones ends with the projectum deliverable, optional

	:type: dict, optional

		:uuid: string, a universally unique id for the task so it can be referenced elsewhere, optional
		:due_date: ['date', 'string'], due date of milestone, yyyy-mm-dd, optional
		:name: string, what is the deliverable of milestone, optional
		:notes: list, any notes about the milestone and/or small, non-deliverable to-dos to reach the milestone, optional
		:tasks: list, list of todo uuids to complete the milestone , optional
		:progress: dict, update on the milestone, optional

			:text: string, text description of progress and observations, optional
			:figure: list, token that dereferences a figure or image in group local storage db, optional
			:slides_urls: list, urls to slides describing the development, e.g., Google slides url, optional
		:objective: string, explains goal of the milestone, optional
		:audience: list, list of people attending the meeting.Normally this list is group_members, collaborators, and pi, or some subset of these. if people are invited who are not alreadyin these groups their names or id's can be added explicitly to the list, optional
		:status: string, status of the milestone. Allowed values are {', '.join(PROJECTUM_STATI)}, optional

			Allowed values:
				* proposed
				* converged
				* started
				* backburner
				* paused
				* cancelled
				* finished
				* all
		:type: string, type of milestone deliverable. Allowed values are {', '.join(MILESTONE_TYPES)}, optional

			Allowed values:
				* mergedpr
				* meeting
				* other
				* paper
				* release
				* email
				* handin
				* purchase
				* approval
				* presentation
				* report
				* submission
				* decision
				* demo
				* skel
		:end_date: ['date', 'string'], end date of milestone, yyyy-mm-dd, optional
		:identifier: string, label of milestone, optional
:name: string, name of the projectum, optional
:notes: list, notes about the projectum, optional
:other_urls: list, link to remote repository. e.g. analysis or data repositories, optional
:pi_id: string, id of the PI, optional
:product_url: string, url for manuscript or code repository, optional
:status: string, status of the projectum. Allowed values are {', '.join(PROJECTUM_STATI)}, required

	Allowed values:
		* proposed
		* converged
		* started
		* backburner
		* paused
		* cancelled
		* finished
		* all
:supplementary_info_urls: list, list of urls that are links to repos gdocs, etc. that contain supplementary info such as data or code snippets, optional


YAML Example
------------

.. code-block:: yaml

	ab_inactive:
	  begin_date: '2020-05-03'
	  deliverable:
	    due_date: '2021-05-03'
	    status: paused
	  description: a prum that has various inactive states in milestones and overall
	  grants: dmref15
	  kickoff:
	    due_date: '2021-05-03'
	    name: Kickoff
	    status: backburner
	    type: meeting
	  lead: abeing
	  milestones:
	    - due_date: '2021-05-03'
	      name: Milestone
	      status: converged
	      uuid: milestone_uuid_inactive
	  status: backburner
	pl_firstprojectum:
	  begin_date: '2020-07-25'
	  deliverable:
	    due_date: '2021-08-26'
	    status: finished
	  end_date: '2020-07-27'
	  kickoff:
	    due_date: '2021-08-03'
	    name: Kickoff
	    status: backburner
	  lead: pliu
	  milestones:
	    - due_date: '2021-08-03'
	      name: Milestone
	      status: converged
	      uuid: milestone_uuid_pl1
	  status: finished
	pl_secondprojectum:
	  begin_date: '2020-07-25'
	  deliverable:
	    due_date: '2021-08-26'
	    status: finished
	  kickoff:
	    due_date: '2021-08-03'
	    name: Kickoff
	    status: backburner
	  lead: pliu
	  milestones:
	    - due_date: '2021-08-03'
	      name: Milestone
	      status: converged
	      uuid: milestone_uuid_pl2
	  status: proposed
	pl_thirdprojectum:
	  begin_date: '2020-07-25'
	  deliverable:
	    due_date: '2021-08-26'
	    status: finished
	  kickoff:
	    due_date: '2021-08-03'
	    name: Kickoff
	    status: backburner
	  lead: pliu
	  milestones:
	    - due_date: '2021-08-03'
	      name: Milestone
	      status: converged
	      uuid: milestone_uuid_pl3
	  status: backburner
	sb_firstprojectum:
	  begin_date: '2020-04-28'
	  collaborators:
	    - aeinstein
	    - pdirac
	  deliverable:
	    audience:
	      - beginning grad in chemistry
	    due_date: '2021-05-05'
	    notes:
	      - deliverable note
	    platform: description of how and where the audience will access the deliverable.  Journal
	      if it is a paper
	    roll_out:
	      - steps that the audience will take to access and interact with the deliverable
	      - not needed for paper submissions
	    scope:
	      - UCs that are supported or some other scope description if it is software
	      - sketch of science story if it is paper
	    status: proposed
	    success_def: audience is happy
	  description: My first projectum
	  grants: SymPy-1.1
	  group_members:
	    - ascopatz
	  kickoff:
	    audience:
	      - lead
	      - pi
	      - group_members
	    date: '2020-05-05'
	    due_date: '2020-05-06'
	    end_date: '2020-05-07'
	    name: Kick off meeting
	    notes:
	      - kickoff note
	    objective: introduce project to the lead
	    status: finished
	  lead: ascopatz
	  log_url: https://docs.google.com/document/d/1YC_wtW5Q
	  milestones:
	    - audience:
	        - lead
	        - pi
	        - group_members
	      due_date: '2020-05-20'
	      name: Project lead presentation
	      notes:
	        - do background reading
	        - understand math
	      objective: lead presents background reading and initial project plan
	      progress:
	        figure:
	          - token that dereferences a figure or image in group local storage db
	        slides_urls:
	          - url to slides describing the development, e.g. Google slides url
	        text: The samples have been synthesized and places in the sample cupboard.
	          They turned out well and are blue as expected
	      status: proposed
	      tasks:
	        - 1saefadf-wdaagea2
	      type: meeting
	      uuid: milestone_uuid_sb1
	    - audience:
	        - lead
	        - pi
	        - group_members
	      due_date: '2020-05-27'
	      name: planning meeting
	      objective: develop a detailed plan with dates
	      status: proposed
	      type: mergedpr
	      uuid: milestone_uuid_sb1_2
	  name: First Projectum
	  other_urls:
	    - https://docs.google.com/document/d/analysis
	  pi_id: scopatz
	  product_url: https://docs.google.com/document/d/manuscript
	  status: started
	  supplementary_info_urls:
	    - https://google.com
	    - https://nytimes.com


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "ab_inactive",
	    "begin_date": "2020-05-03",
	    "deliverable": {
	        "due_date": "2021-05-03",
	        "status": "paused"
	    },
	    "description": "a prum that has various inactive states in milestones and overall",
	    "grants": "dmref15",
	    "kickoff": {
	        "due_date": "2021-05-03",
	        "name": "Kickoff",
	        "status": "backburner",
	        "type": "meeting"
	    },
	    "lead": "abeing",
	    "milestones": [
	        {
	            "due_date": "2021-05-03",
	            "name": "Milestone",
	            "status": "converged",
	            "uuid": "milestone_uuid_inactive"
	        }
	    ],
	    "status": "backburner"
	}
	{
	    "_id": "pl_firstprojectum",
	    "begin_date": "2020-07-25",
	    "deliverable": {
	        "due_date": "2021-08-26",
	        "status": "finished"
	    },
	    "end_date": "2020-07-27",
	    "kickoff": {
	        "due_date": "2021-08-03",
	        "name": "Kickoff",
	        "status": "backburner"
	    },
	    "lead": "pliu",
	    "milestones": [
	        {
	            "due_date": "2021-08-03",
	            "name": "Milestone",
	            "status": "converged",
	            "uuid": "milestone_uuid_pl1"
	        }
	    ],
	    "status": "finished"
	}
	{
	    "_id": "pl_secondprojectum",
	    "begin_date": "2020-07-25",
	    "deliverable": {
	        "due_date": "2021-08-26",
	        "status": "finished"
	    },
	    "kickoff": {
	        "due_date": "2021-08-03",
	        "name": "Kickoff",
	        "status": "backburner"
	    },
	    "lead": "pliu",
	    "milestones": [
	        {
	            "due_date": "2021-08-03",
	            "name": "Milestone",
	            "status": "converged",
	            "uuid": "milestone_uuid_pl2"
	        }
	    ],
	    "status": "proposed"
	}
	{
	    "_id": "pl_thirdprojectum",
	    "begin_date": "2020-07-25",
	    "deliverable": {
	        "due_date": "2021-08-26",
	        "status": "finished"
	    },
	    "kickoff": {
	        "due_date": "2021-08-03",
	        "name": "Kickoff",
	        "status": "backburner"
	    },
	    "lead": "pliu",
	    "milestones": [
	        {
	            "due_date": "2021-08-03",
	            "name": "Milestone",
	            "status": "converged",
	            "uuid": "milestone_uuid_pl3"
	        }
	    ],
	    "status": "backburner"
	}
	{
	    "_id": "sb_firstprojectum",
	    "begin_date": "2020-04-28",
	    "collaborators": [
	        "aeinstein",
	        "pdirac"
	    ],
	    "deliverable": {
	        "audience": [
	            "beginning grad in chemistry"
	        ],
	        "due_date": "2021-05-05",
	        "notes": [
	            "deliverable note"
	        ],
	        "platform": "description of how and where the audience will access the deliverable.  Journal if it is a paper",
	        "roll_out": [
	            "steps that the audience will take to access and interact with the deliverable",
	            "not needed for paper submissions"
	        ],
	        "scope": [
	            "UCs that are supported or some other scope description if it is software",
	            "sketch of science story if it is paper"
	        ],
	        "status": "proposed",
	        "success_def": "audience is happy"
	    },
	    "description": "My first projectum",
	    "grants": "SymPy-1.1",
	    "group_members": [
	        "ascopatz"
	    ],
	    "kickoff": {
	        "audience": [
	            "lead",
	            "pi",
	            "group_members"
	        ],
	        "date": "2020-05-05",
	        "due_date": "2020-05-06",
	        "end_date": "2020-05-07",
	        "name": "Kick off meeting",
	        "notes": [
	            "kickoff note"
	        ],
	        "objective": "introduce project to the lead",
	        "status": "finished"
	    },
	    "lead": "ascopatz",
	    "log_url": "https://docs.google.com/document/d/1YC_wtW5Q",
	    "milestones": [
	        {
	            "audience": [
	                "lead",
	                "pi",
	                "group_members"
	            ],
	            "due_date": "2020-05-20",
	            "name": "Project lead presentation",
	            "notes": [
	                "do background reading",
	                "understand math"
	            ],
	            "objective": "lead presents background reading and initial project plan",
	            "progress": {
	                "figure": [
	                    "token that dereferences a figure or image in group local storage db"
	                ],
	                "slides_urls": [
	                    "url to slides describing the development, e.g. Google slides url"
	                ],
	                "text": "The samples have been synthesized and places in the sample cupboard. They turned out well and are blue as expected"
	            },
	            "status": "proposed",
	            "tasks": [
	                "1saefadf-wdaagea2"
	            ],
	            "type": "meeting",
	            "uuid": "milestone_uuid_sb1"
	        },
	        {
	            "audience": [
	                "lead",
	                "pi",
	                "group_members"
	            ],
	            "due_date": "2020-05-27",
	            "name": "planning meeting",
	            "objective": "develop a detailed plan with dates",
	            "status": "proposed",
	            "type": "mergedpr",
	            "uuid": "milestone_uuid_sb1_2"
	        }
	    ],
	    "name": "First Projectum",
	    "other_urls": [
	        "https://docs.google.com/document/d/analysis"
	    ],
	    "pi_id": "scopatz",
	    "product_url": "https://docs.google.com/document/d/manuscript",
	    "status": "started",
	    "supplementary_info_urls": [
	        "https://google.com",
	        "https://nytimes.com"
	    ]
	}

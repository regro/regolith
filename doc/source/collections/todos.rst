Todos
=====
This is a collection of todo items

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, the person to whom these todos are applied.this should be the id of a person from people, required
:todos: list, a list of the todo tasks, optional

	:type: dict, optional

		:uuid: string, a universally unique id for the task so it can be referenced elsewhere, optional
		:assigned_by: string, ID of the member that assigns the task, optional
		:begin_date: ['string', 'date'], the begin date, optional
		:end_date: ['string', 'date'], the end date, optional
		:deadline: boolean, true if the due date is a hard deadline, optional
		:description: string, the description of the to-do task, optional
		:due_date: ['string', 'date'], the due date, optional
		:duration: float, the size of the task/ the estimated duration it will take to finish the task. Unit: miniutes., optional
		:importance: integer, the importance, from 0 to 3, optional
		:status: string, the status: started/finished/cancelled, optional

			Allowed values:
				* started
				* finished
				* cancelled
				* paused
		:notes: list, additional notes for this task, optional

			:type: string, optional
		:running_index: integer, Index of a certain task used to update that task in the enumerated todo list., optional
		:tags: list, user-defined tags that can be used to filter tasks, optional


YAML Example
------------

.. code-block:: yaml

	ascopatz: {}
	sbillinge:
	  todos:
	    - assigned_by: scopatz
	      begin_date: '2020-06-15'
	      deadline: true
	      description: read paper
	      due_date: '2020-07-19'
	      duration: 60.0
	      importance: 2
	      running_index: 1
	      status: started
	      tags:
	        - reading
	        - downtime
	      uuid: 1saefadf-wdaagea2
	    - assigned_by: sbillinge
	      begin_date: '2020-06-22'
	      description: prepare the presentation
	      due_date: '2020-07-29'
	      duration: 30.0
	      importance: 0
	      notes:
	        - about 10 minutes
	        - don't forget to upload to the website
	      running_index: 2
	      status: started
	      tags:
	        - downtime
	      uuid: 2saefadf-wdaagea3


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "ascopatz"
	}
	{
	    "_id": "sbillinge",
	    "todos": [
	        {
	            "assigned_by": "scopatz",
	            "begin_date": "2020-06-15",
	            "deadline": true,
	            "description": "read paper",
	            "due_date": "2020-07-19",
	            "duration": 60.0,
	            "importance": 2,
	            "running_index": 1,
	            "status": "started",
	            "tags": [
	                "reading",
	                "downtime"
	            ],
	            "uuid": "1saefadf-wdaagea2"
	        },
	        {
	            "assigned_by": "sbillinge",
	            "begin_date": "2020-06-22",
	            "description": "prepare the presentation",
	            "due_date": "2020-07-29",
	            "duration": 30.0,
	            "importance": 0,
	            "notes": [
	                "about 10 minutes",
	                "don't forget to upload to the website"
	            ],
	            "running_index": 2,
	            "status": "started",
	            "tags": [
	                "downtime"
	            ],
	            "uuid": "2saefadf-wdaagea3"
	        }
	    ]
	}

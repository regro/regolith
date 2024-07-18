Expenses
========
This collection records expenses for the group. It should most likely be private

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, short representation, such as this-is-my-name, required

	Allowed values: 
		* travel
		* business
:grant_percentages: list, the percentage of the reimbursement amount to put on each grant. This list must be the same length asthe grants list and the percentages placed in the order that the grants appear in that list, optional
:grants: ['string', 'list'], the grants in a list, or a string if only one grant, required
:itemized_expenses: list, optional

	:type: dict, optional

		:day: integer, Expense day, optional
		:month: ['string', 'integer'], Expense month, optional
		:year: integer, Expense year, optional
		:purpose: string, reason for expense, optional
		:unsegregated_expense: float, The allowed expenses, optional
		:segregated_expense: float, The unallowed expenses, optional
		:original_currency: float, The currency the payment was made in, optional
:overall_purpose: string, The reason for the expenses, required
:payee: string, The name or id of the payee filing the expense, required
:project: ['string', 'list'], project or list of projects that this presentation is associated with.  Should be discoverable in projects collection, required


YAML Example
------------

.. code-block:: yaml

	test:
	  expense_type: business
	  grant_percentages:
	    - '50'
	    - '50'
	  grants:
	    - dmref15
	    - SymPy-1.1
	  itemized_expenses:
	    - day: 1
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 10
	      year: 2018
	    - day: 2
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 20
	      year: 2018
	    - day: 3
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 30
	      year: 2018
	    - day: 4
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 40
	      year: 2018
	    - day: 5
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 50
	      year: 2018
	    - day: 6
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 60
	      year: 2018
	    - day: 7
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 70
	      year: 2018
	    - day: 8
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 80
	      year: 2018
	    - day: 9
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 90
	      year: 2018
	    - day: 10
	      month: Jan
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 100
	      year: 2018
	  overall_purpose: testing the database
	  payee: scopatz
	  project: Cyclus


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "test",
	    "expense_type": "business",
	    "grant_percentages": [
	        "50",
	        "50"
	    ],
	    "grants": [
	        "dmref15",
	        "SymPy-1.1"
	    ],
	    "itemized_expenses": [
	        {
	            "day": 1,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 10,
	            "year": 2018
	        },
	        {
	            "day": 2,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 20,
	            "year": 2018
	        },
	        {
	            "day": 3,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 30,
	            "year": 2018
	        },
	        {
	            "day": 4,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 40,
	            "year": 2018
	        },
	        {
	            "day": 5,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 50,
	            "year": 2018
	        },
	        {
	            "day": 6,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 60,
	            "year": 2018
	        },
	        {
	            "day": 7,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 70,
	            "year": 2018
	        },
	        {
	            "day": 8,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 80,
	            "year": 2018
	        },
	        {
	            "day": 9,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 90,
	            "year": 2018
	        },
	        {
	            "day": 10,
	            "month": "Jan",
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 100,
	            "year": 2018
	        }
	    ],
	    "overall_purpose": "testing the database",
	    "payee": "scopatz",
	    "project": "Cyclus"
	}

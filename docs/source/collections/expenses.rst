Expenses
========
This collection records expenses for the group. It should most likely be private

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, short representation, such as this-is-my-name, required
:begin_date: ['string', 'date'], begin date in YYYY-MM-DD, optional
:begin_day: integer, The day when the travel/business started, optional
:begin_month: ['string', 'integer'], The month when the travel/business started, optional
:begin_year: integer, The year when the travel/business started, optional
:end_date: ['string', 'date'], end date in YYYY-MM-DD, optional
:end_day: integer, The day when the travel/business end, optional
:end_month: ['string', 'integer'], The month when the travel/business end, optional
:end_year: integer, The year when the travel/business end, optional

	Allowed values:
		* travel
		* business
:grant_percentages: list, the percentage of the reimbursement amount to put on each grant. This list must be the same length asthe grants list and the percentages placed in the order that the grants appear in that list, optional
:grants: ['string', 'list'], the grants in a list, or a string if only one grant, required
:itemized_expenses: list, optional

	:type: dict, optional

		:day: integer, Expense day, optional
		:date: ['string', 'date'], Expense date, optional
		:month: ['string', 'integer'], Expense month, optional
		:year: integer, Expense year, optional
		:purpose: string, reason for expense, optional
		:unsegregated_expense: float, The allowed expenses, optional
		:segregated_expense: float, The unallowed expenses, optional
		:currency: string, The currency the payment was made in, optional
		:prepaid_expense: float, The amount of prepaid expense in USD, optional
		:notes: ['list', 'string'], notes about the expense, optional
:notes: ['list', 'string'], Description of the expenses. It will not be included in the reimbursement form, optional
:overall_purpose: string, The reason for the expenses, required
:payee: string, The name or id of the payee filing the expense, required
:project: ['string', 'list'], project or list of projects that this presentation is associated with.  Should be discoverable in projects collection, optional
:reimbursements: list, Reimbursements for the expense, optional

	:type: dict, optional

		:amount: float, amount for reimbursements, optional
		:date: ['string', 'date'], date of reimbursement, optional
		:submission_date: ['string', 'date'], date of submission, optional
		:submission_day: integer, day of submission. deprecated but here for backwards compatibility, optional
		:submission_month: ['integer', 'string'], month of submission. deprecated but here for backwards compatibility, optional
		:submission_year: integer, year of submission. deprecated but here for backwards compatibility, optional
		:day: integer, day of reimbursement. deprecated but here for backwards compatibility, optional
		:month: ['string', 'integer'], month of reimbursement. deprecated but here for backwards compatibility, optional
		:year: integer, year of reimbursement. deprecated but here for backwards compatibility, optional
		:where: string, where the reimbursement has been sent, optional
:status: string, The status of the expense, optional

	Allowed values:
		* unsubmitted
		* submitted
		* reimbursed
		* declined


YAML Example
------------

.. code-block:: yaml

	test:
	  begin_date: '2018-01-01'
	  end_date: '2018-01-10'
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
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 10
	      year: 2018
	    - day: 2
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 20
	      year: 2018
	    - day: 3
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 30
	      year: 2018
	    - day: 4
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 40
	      year: 2018
	    - day: 5
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 50
	      year: 2018
	    - day: 6
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 60
	      year: 2018
	    - day: 7
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 70
	      year: 2018
	    - day: 8
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 80
	      year: 2018
	    - day: 9
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 90
	      year: 2018
	    - day: 10
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 100
	      year: 2018
	  notes: this expense was used to get the work done
	  overall_purpose: testing the databallectionsse
	  payee: scopatz
	  project: Cyclus
	  reimbursements:
	    - amount: 500
	      date: tbd
	      submission_date: tbd
	      where: Columbia
	    - amount: 1000
	      date: '2019-02-15'
	      submission_date: '2019-09-05'
	      where: Columbia
	  status: submitted
	test2:
	  begin_date: '2019-01-01'
	  end_date: '2019-01-10'
	  expense_type: business
	  grant_percentages:
	    - '100'
	  grants:
	    - SymPy-1.1
	  itemized_expenses:
	    - currency: USD
	      day: 2
	      month: Jan
	      notes:
	        - this is just a test
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 10
	      year: 2019
	  notes: some note
	  overall_purpose: testing
	  payee: sbillinge
	  project: reimbursed expense
	  reimbursements:
	    - amount: 100
	      date: '2019-09-15'
	      submission_date: tbd
	      where: Columbia
	  status: reimbursed
	test3:
	  begin_date: '2020-01-01'
	  end_date: '2020-01-10'
	  expense_type: business
	  grant_percentages:
	    - '100'
	  grants:
	    - SymPy-1.1
	  itemized_expenses:
	    - day: 3
	      month: Jan
	      prepaid_expense: 10.3
	      purpose: test
	      segregated_expense: 0
	      unsegregated_expense: 10
	      year: 2020
	  notes: some other note
	  overall_purpose: more testing
	  payee: sbillinge
	  project: reimbursed expense
	  reimbursements:
	    - amount: 100
	      date: '2020-09-15'
	      submission_date: tbd
	      where: Columbia
	  status: bad_status


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "test",
	    "begin_date": "2018-01-01",
	    "end_date": "2018-01-10",
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
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 10,
	            "year": 2018
	        },
	        {
	            "day": 2,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 20,
	            "year": 2018
	        },
	        {
	            "day": 3,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 30,
	            "year": 2018
	        },
	        {
	            "day": 4,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 40,
	            "year": 2018
	        },
	        {
	            "day": 5,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 50,
	            "year": 2018
	        },
	        {
	            "day": 6,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 60,
	            "year": 2018
	        },
	        {
	            "day": 7,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 70,
	            "year": 2018
	        },
	        {
	            "day": 8,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 80,
	            "year": 2018
	        },
	        {
	            "day": 9,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 90,
	            "year": 2018
	        },
	        {
	            "day": 10,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 100,
	            "year": 2018
	        }
	    ],
	    "notes": "this expense was used to get the work done",
	    "overall_purpose": "testing the databallectionsse",
	    "payee": "scopatz",
	    "project": "Cyclus",
	    "reimbursements": [
	        {
	            "amount": 500,
	            "date": "tbd",
	            "submission_date": "tbd",
	            "where": "Columbia"
	        },
	        {
	            "amount": 1000,
	            "date": "2019-02-15",
	            "submission_date": "2019-09-05",
	            "where": "Columbia"
	        }
	    ],
	    "status": "submitted"
	}
	{
	    "_id": "test2",
	    "begin_date": "2019-01-01",
	    "end_date": "2019-01-10",
	    "expense_type": "business",
	    "grant_percentages": [
	        "100"
	    ],
	    "grants": [
	        "SymPy-1.1"
	    ],
	    "itemized_expenses": [
	        {
	            "currency": "USD",
	            "day": 2,
	            "month": "Jan",
	            "notes": [
	                "this is just a test"
	            ],
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 10,
	            "year": 2019
	        }
	    ],
	    "notes": "some note",
	    "overall_purpose": "testing",
	    "payee": "sbillinge",
	    "project": "reimbursed expense",
	    "reimbursements": [
	        {
	            "amount": 100,
	            "date": "2019-09-15",
	            "submission_date": "tbd",
	            "where": "Columbia"
	        }
	    ],
	    "status": "reimbursed"
	}
	{
	    "_id": "test3",
	    "begin_date": "2020-01-01",
	    "end_date": "2020-01-10",
	    "expense_type": "business",
	    "grant_percentages": [
	        "100"
	    ],
	    "grants": [
	        "SymPy-1.1"
	    ],
	    "itemized_expenses": [
	        {
	            "day": 3,
	            "month": "Jan",
	            "prepaid_expense": 10.3,
	            "purpose": "test",
	            "segregated_expense": 0,
	            "unsegregated_expense": 10,
	            "year": 2020
	        }
	    ],
	    "notes": "some other note",
	    "overall_purpose": "more testing",
	    "payee": "sbillinge",
	    "project": "reimbursed expense",
	    "reimbursements": [
	        {
	            "amount": 100,
	            "date": "2020-09-15",
	            "submission_date": "tbd",
	            "where": "Columbia"
	        }
	    ],
	    "status": "bad_status"
	}

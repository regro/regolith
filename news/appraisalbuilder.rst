**Added:**
* a builder for annual appraisals modelled on columbia SEAS appraisal
* a tool in tools in tools.py that will merge two collections, similar to chainDB but they collections are not public/private versions of the same collection but collections of different names.  Intitiall intended for proposals and grants so that when a proposal gets funded its info doesn't have to be copied over to the grant but can be dereferenced
* a convenience tool to tools.py that gets all the date items (begin_day, end_year, month, etc.) from an entry and returns them as a dict
* a bunch of bespoke filters to tools.py that return different things from different collections
* a function that takes regolith dates and returns the beginning and ending date from a document
* tests for functions in regolith.dates

**Changed:** None

**Deprecated:** None

**Removed:** None

**Fixed:**
* bug in date_to_float removes extra zero in day float value

**Security:** None

**Added:**
 - merge_collections to tools.py.  merges two collections

**Changed:**
 - current and pending builder extended to build c+p from merged proposal and grants collections
 - added filter for cppflag so you can have current grants that don't appear in the current and pending form by setting cppflag to false in the db

**Deprecated:** None

**Removed:** None

**Fixed:**
 - cpbuilder does name comparison on fuzzy-searched name for standardization
 - cpbuilder includes initials when it is a multi-pi grant
 - filter_grants in tools.py bug fixed that incorrectly reassigns team members
 - updated docstring on filter_grants to make it clearer

**Security:** None

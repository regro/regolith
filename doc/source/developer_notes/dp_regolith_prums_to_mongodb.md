This document contains methodological information about the dp_regolith_prums_to_mongodb prum worked on by lead: dpeters.

# NOTES

- Initial hypothesis is that the latency introduced by the file system (fs) backend of the regolith software is due to the
  database rc calls that load the entire database before query or CRUD ops.
- a_projectum was chosen to test this hypothesis because the helper adder code is easier to work with than the code for other
- helpers (e.g., listers, updaters).
- Code modifications that limit/delete all database loading protocols are documented in the following tables. The modifications
  serve as a basis for the methodology used to diagnose the regolith latency issue.
- All trials were profiled using python's cProfiler and the .html files have been linked to the dp_regolith_prums_to_mongodb
  document in projecta.yml.
- We were able to conclude that the database loading protocols for a_projectum cause latency on the fs backend. Separately,
  the connection configuration architecture causes latency on the MongoDB backend.

## FS CLIENT TRIALS

**trials 1-20**

| script               | line | new code | avg. total execution time |
| -------------------- | ---- | -------- | ------------------------- |
| a_projectumhelper.py |      | no mod   | **11.832 s**              |

**trials 21-40**

| script               | line | new code                                                     | avg. total execution time |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------- |
| a_projectumhelper.py | 90   | # gtx[rc.coll] = sorted(                                     | **11.654 s**              |
|                      | 91   | # all_docs_from_collection(rc.client, rc.coll), key=\_id_key |
|                      | 92   | # )                                                          |
|                      | 93   | gtx[rc.coll] = [{"_id": "hold"}]                             |
|                      | 94   | # gtx["all_docs_from_collection"] = all_docs_from_collection |

**trials 41-60**

| script               | line | new code                                                     | avg. total execution time |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------- |
| a_projectumhelper.py | 86   | rc.pi_id = "sbillinge"                                       | **2.348 s**               |
|                      | 90   | # gtx[rc.coll] = sorted(                                     |
|                      | 91   | # all_docs_from_collection(rc.client, rc.coll), key=\_id_key |
|                      | 92   | # )                                                          |
|                      | 93   | gtx[rc.coll] = [{"_id": "hold"}]                             |
|                      | 94   | # gtx["all_docs_from_collection"] = all_docs_from_collection |
| database.xsh         | 179  | for k, v in coll:                                            |
| fsclient.py          | 92   | docs = {}                                                    |
|                      | 94   | for \_id, doc in docs:                                       |

## MONGODB CLIENT TRIALS

**trials 1-20**

| script               | line | new code | avg. total execution time |
| -------------------- | ---- | -------- | ------------------------- |
| a_projectumhelper.py |      | no mod   | **3.606 s**               |

**trials 21-40**

| script               | line | new code                                                     | avg. total execution time |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------- |
| a_projectumhelper.py | 90   | # gtx[rc.coll] = sorted(                                     | **3.698 s**               |
|                      | 91   | # all_docs_from_collection(rc.client, rc.coll), key=\_id_key |
|                      | 92   | # )                                                          |
|                      | 93   | gtx[rc.coll] = [{"_id": "hold"}]                             |
|                      | 94   | # gtx["all_docs_from_collection"] = all_docs_from_collection |

**trials 41-60**

| script               | line | new code                                                     | avg. total execution time |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------- |
| a_projectumhelper.py | 90   | # gtx[rc.coll] = sorted(                                     | **3.390 s**               |
|                      | 91   | # all_docs_from_collection(rc.client, rc.coll), key=\_id_key |
|                      | 92   | # )                                                          |
|                      | 93   | gtx[rc.coll] = [{"_id": "hold"}]                             |
|                      | 94   | # gtx["all_docs_from_collection"] = all_docs_from_collection |
| mongoclient.py       | 164  | # return {                                                   |
|                      | 165  | # doc['_id']: doc for doc in col.find({})                    |
|                      | 166  | # }                                                          |
|                      | 167  | return {}                                                    |

**trials 61-80**

| script               | line | new code                                                     | avg. total execution time |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------- |
| a_projectumhelper.py | 86   | rc.pi_id = "sbillinge"                                       | **2.939 s**               |
|                      | 90   | # gtx[rc.coll] = sorted(                                     |
|                      | 91   | # all_docs_from_collection(rc.client, rc.coll), key=\_id_key |
|                      | 92   | # )                                                          |
|                      | 93   | gtx[rc.coll] = [{"_id": "hold"}]                             |
|                      | 94   | # gtx["all_docs_from_collection"] = all_docs_from_collection |
| database.xsh         | 179  | for k, v in coll:                                            |
| fsclient.py          | 92   | docs = {}                                                    |
|                      | 94   | for \_id, doc in docs:                                       |
| mongoclient.py       | 164  | # return {                                                   |
|                      | 165  | # doc['_id']: doc for doc in col.find({})                    |
|                      | 166  | # }                                                          |
|                      | 167  | return {}                                                    |

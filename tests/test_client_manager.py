import pytest
import os
from copy import deepcopy, copy

from regolith.database import connect
from regolith.runcontrol import DEFAULT_RC, load_rcfile
from regolith.tools import all_docs_from_collection
from regolith.schemas import EXEMPLARS


def test_collection_retrieval_python(make_mixed_db):
    if make_mixed_db is False:
        pytest.skip("Mongoclient failed to start")
    else:
        repo, fs_coll, mongo_coll = make_mixed_db
    os.chdir(repo)
    rc = copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    with connect(rc) as rc.client:
        fs_test_dict = dict(list(all_docs_from_collection(rc.client, "abstracts"))[0])
        mongo_test_dict = dict(list(all_docs_from_collection(rc.client, "assignments"))[0])
    fs_expected_dict = deepcopy(EXEMPLARS[fs_coll])
    mongo_expected_dict = deepcopy(EXEMPLARS[mongo_coll])
    assert fs_test_dict == fs_expected_dict
    assert mongo_test_dict == mongo_expected_dict

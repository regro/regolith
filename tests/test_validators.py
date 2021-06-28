from collections.abc import Sequence
from pathlib import Path
import os
import copy

import pytest

from regolith.schemas import SCHEMAS, validate, EXEMPLARS
from pprint import pprint


@pytest.mark.parametrize("key", SCHEMAS.keys())
def test_validation(key):
    if isinstance(EXEMPLARS[key], Sequence):
        for e in EXEMPLARS[key]:
            validate(key, e, SCHEMAS)
    else:
        validate(key, EXEMPLARS[key], SCHEMAS)


@pytest.mark.parametrize("key", SCHEMAS.keys())
def test_exemplars(key):
    if isinstance(EXEMPLARS[key], Sequence):
        for e in EXEMPLARS[key]:
            v = validate(key, e, SCHEMAS)
            assert v[0]
    else:
        v = validate(key, EXEMPLARS[key], SCHEMAS)
        if not v[0]:
            for vv, reason in v[1].items():
                print(vv, reason)
                print(type(EXEMPLARS[key][vv]))
                pprint(EXEMPLARS[key][vv])
        assert v[0]


BAD_PROJECTUM = {
    "_id": "sb_firstprojectum",
    "begin_date": "2020-04-28",
    "collaborators": ["aeinstein", "pdirac"],
    "deliverable": {
        "audience": ["beginning grad in chemistry"],
        "due_date": "2021-05-05",
        "success_def": "audience is happy",
        "scope": ["UCs that are supported or some other scope description "
                  "if it is software", "sketch of science story if it is paper"
                  ],
        "platform": "description of how and where the audience will access "
                    "the deliverable.  Journal if it is a paper",
        "roll_out": [
            "steps that the audience will take to access and interact with "
            "the deliverable", "not needed for paper submissions"],
        "notes": ["deliverable note"],
        "status": "proposed"
    }
}


def test_mongo_invalid_insertion(make_mongodb):
    # proof that valid insertion is allowed is provided by helper tests on mongo
    if make_mongodb is False:
        pytest.skip("Mongoclient failed to start")
    else:
        repo = Path(make_mongodb)
    from regolith.database import connect
    from regolith.runcontrol import DEFAULT_RC, load_rcfile
    os.chdir(repo)
    rc = copy.copy(DEFAULT_RC)
    rc.schemas = SCHEMAS
    rc._update(load_rcfile("regolithrc.json"))
    with connect(rc) as rc.client:
        only_database_in_test = rc.databases[0]['name']
        try:
            rc.client.insert_one(only_database_in_test, 'projecta', BAD_PROJECTUM)
        except ValueError as e:
            result = e.args[0]
    expected = 'ERROR in sb_firstprojectum:\n{\'lead\': [\'required field\'], \'status\': [\'required field\']}\nNone\nNone\n---------------\n'
    assert result == expected

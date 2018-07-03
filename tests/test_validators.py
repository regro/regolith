from collections.abc import Sequence

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

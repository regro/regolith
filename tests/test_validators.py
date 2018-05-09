from pprint import pprint

import pytest

from regolith.schemas import SCHEMAS, validate, EXEMPLARS


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_validation(key):
    if isinstance(EXEMPLARS[key], list):
        for e in EXEMPLARS[key]:
            validate(key, e, SCHEMAS)
    else:
        validate(key, EXEMPLARS[key], SCHEMAS)


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_exemplars(key):
    if isinstance(EXEMPLARS[key], list):
        for e in EXEMPLARS[key]:
            v = validate(key, e, SCHEMAS)
            assert v[0]
    else:
        v = validate(key, EXEMPLARS[key], SCHEMAS)
        assert v[0]

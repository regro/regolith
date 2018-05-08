from pprint import pprint

import pytest

from regolith.schemas import SCHEMAS, validate, EXEMPLARS


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_validation(key):
    validate(key, EXEMPLARS[key], SCHEMAS)


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_exemplars(key):
    v = validate(key, EXEMPLARS[key], SCHEMAS)
    pprint(v[1])
    assert v[0]

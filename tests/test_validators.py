import pytest

from regolith.schemas import SCHEMAS, validate, EXEMPLARS


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_validation(key):
    b, err = validate(key, EXEMPLARS[key])
    print(err)
    assert b

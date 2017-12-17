import pytest

from regolith.exemplars import EXEMPLARS
from regolith.schemas import SCHEMAS
from regolith.validators import validate


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_validation(key):
    validate(key, EXEMPLARS[key])



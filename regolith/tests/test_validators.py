from regolith.validators import validate_schema
from regolith.schemas import SCHEMAS
from regolith.exemplars import EXEMPLARS
import pytest


@pytest.mark.parametrize('key', SCHEMAS.keys())
def test_validation(key):
    validate_schema(EXEMPLARS[key], SCHEMAS[key], (key,))



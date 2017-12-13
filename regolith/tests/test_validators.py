from regolith.validators import validate_schema
from regolith.schemas.schemas import schemas
import json
from io import StringIO


def test_grant_validation():
    raw_json = """{"_id": "SymPy-1.1",
     "amount": 3000.0,
     "begin_day": 1,
     "begin_month": "May",
     "begin_year": 2017,
     "call_for_proposals": "https://groups.google.com/d/msg/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ",
     "end_day": 31,
     "end_month": "December",
     "end_year": 2017,
     "funder": "NumFOCUS",
     "narrative": "https://docs.google.com/document/d/1nZxqoL-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp=sharing",
     "program": "Small Development Grants",
     "team": [{"institution": "University of South Carolina",
               "name": "Anthony Scopatz",
               "position": "PI"},
              {"institution": "University of South Carolina",
               "name": "Aaron Meurer",
               "position": "researcher"}
            ],
     "title": "SymPy 1.1 Release Support"}"""
    record = json.loads(raw_json)
    validate_schema(record, schemas['grants'])



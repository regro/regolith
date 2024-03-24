import datetime

import tempfile
from pathlib import Path

from regolith.fsclient import date_encoder, dump_json


def test_date_encoder():
    day = datetime.date(2021,1,1)
    time = datetime.datetime(2021, 5, 18, 6, 28, 21, 504549)
    assert date_encoder(day) == '2021-01-01'
    assert date_encoder(time) == '2021-05-18T06:28:21.504549'

def test_dump_json():
    doc = {"first": {"_id": "first", "name": "me", "date": datetime.date(2021,5,1),
           "test_list": [5, 4]},
           "second": {"_id": "second"}
           }
    json_doc = ('{"_id": "first", "date": "2021-05-01", "name": "me", "test_list": [5, 4]}\n{"_id": "second"}')
    temp_dir = Path(tempfile.gettempdir())
    filename = temp_dir / "test.json"
    dump_json(filename, doc, date_handler=date_encoder)
    with open(filename, 'r', encoding="utf-8") as f:
        actual = f.read()
    assert actual == json_doc

# datasets = [
#     (
#         {"first": {"date": "2021-05-01", "name": "me", "test_list": [5, 4]}, "second": {}},
#         {
#             "first": {"_id": "first", "name": "me", "date": datetime.date(2021, 5, 1), "test_list": [5, 4]},
#             "second": {"_id": "second"},
#         },
#     ),
# ]
# @pytest.mark.parametrize("json_doc, expected", datasets)
# def test_load_json(json_doc, expected):
#     temp_dir = Path(tempfile.gettempdir())
#     filename = temp_dir / "test.json"
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(json_doc, f)
#     actual = load_json(filename)
#     assert actual == expected

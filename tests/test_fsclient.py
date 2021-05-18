import datetime
from regolith.fsclient import date_encoder

def test_date_encoder():
    day = datetime.date(2021,1,1)
    time = datetime.datetime(2021, 5, 18, 6, 28, 21, 504549)
    assert date_encoder(day) == '2021-01-01'
    assert date_encoder(time) == '2021-05-18T06:28:21.504549'

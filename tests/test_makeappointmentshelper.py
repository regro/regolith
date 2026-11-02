"""Tests for the makeappointments helper on a small group of its own."""

import json
import os

import pytest

from regolith.fsclient import dump_yaml
from regolith.main import main

GRANTS = {
    "keck": {
        "_id": "keck",
        "alias": "Keck",
        "title": "A Keck grant",
        "amount": 1.0,
        "funder": "Keck",
        "team": [],
        "begin_date": "2025-07-01",
        "end_date": "2027-06-30",
        "budget": [
            {"begin_date": "2025-07-01", "end_date": "2027-06-30", "student_months": 24, "ss_months": 6},
        ],
    },
    "diffai": {
        "_id": "diffai",
        "alias": "diffai",
        "title": "A grant with no budget",
        "amount": 1.0,
        "funder": "NSF",
        "team": [],
        "begin_date": "2025-09-01",
        "end_date": "2028-08-31",
    },
    "old": {
        "_id": "old",
        "alias": "old",
        "title": "A grant that has ended",
        "amount": 1.0,
        "funder": "DOE",
        "team": [],
        "begin_date": "2022-01-01",
        "end_date": "2024-12-31",
        "budget": [{"begin_date": "2022-01-01", "end_date": "2024-12-31", "student_months": 36}],
    },
}
PEOPLE = {
    "stu": {
        "_id": "stu",
        "name": "A Student",
        "appointments": {
            "y24": {
                "begin_date": "2024-01-01",
                "end_date": "2024-12-31",
                "type": "gra",
                "loading": 1.0,
                "grant": "old",
            },
            "y25": {
                "begin_date": "2025-07-01",
                "end_date": "2026-06-30",
                "type": "gra",
                "loading": 1.0,
                "grant": "KECK",
            },
            "f26": {
                "begin_date": "2026-07-01",
                "end_date": "2026-12-31",
                "type": "gra",
                "loading": 1.0,
                "grant": "diffai",
            },
            "w27": {
                "begin_date": "2027-01-01",
                "end_date": "2027-03-31",
                "type": "gra",
                "loading": 1.0,
                "grant": "nogrant",
            },
        },
    }
}


@pytest.fixture
def group_db(tmp_path):
    cwd = os.getcwd()
    rc = {
        "groupname": "ERGS",
        "databases": [
            {
                "name": "test",
                "url": str(tmp_path),
                "public": False,
                "path": "db",
                "local": True,
                "backend": "filesystem",
            }
        ],
    }
    (tmp_path / "regolithrc.json").write_text(json.dumps(rc))
    (tmp_path / "db").mkdir()
    dump_yaml(str(tmp_path / "db" / "grants.yaml"), json.loads(json.dumps(GRANTS)))
    dump_yaml(str(tmp_path / "db" / "people.yaml"), json.loads(json.dumps(PEOPLE)))
    dump_yaml(str(tmp_path / "db" / "proposals.yaml"), {})
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


# Test that grants are found whatever case an appointment names them in, and that grants with no budget and
# grants not in the collection are reported together instead of stopping the run
def test_makeappointments_reports_grant_problems(group_db, capsys):
    main(["helper", "makeappointments", "run", "--no-plot", "--projection-from-date", "2026-01-01"])
    output = capsys.readouterr().out
    expected_reports = [
        "appointments on grants not in the grants collection (check the grant id or alias):\n"
        "    person: stu, appointment: w27, grant: nogrant\n",
        "grants with appointments but no budget, so their spending is not known: diffai\n",
    ]
    for expected_report in expected_reports:
        assert expected_report in output
    assert "KECK" not in output and "keck" not in output.split("underspent grants:")[0]


# Test that only grants running on or after the projection date are plotted, unless --verbose is given
@pytest.mark.parametrize(
    "extra_args, expected_titles",
    [
        # C1: a projection date after the old grant ended, expect only the current grant plotted
        pytest.param([], ["Keck"], id="current-only"),
        # C2: --verbose, expect the ended grant plotted too
        pytest.param(["--verbose"], ["Keck", "old"], id="verbose"),
    ],
)
def test_makeappointments_plots(extra_args, expected_titles, group_db, monkeypatch):
    titles = []
    from regolith.helpers import makeappointmentshelper

    real_plotter = makeappointmentshelper.plotter

    def recording_plotter(*args, title=None, **kwargs):
        titles.append(title)
        return real_plotter(*args, title=title, **kwargs)

    monkeypatch.setattr(makeappointmentshelper, "plotter", recording_plotter)
    main(["helper", "makeappointments", "run", "--no-gui", "--projection-from-date", "2026-01-01", *extra_args])
    grant_titles = [title for title in titles if title not in ("Cumulative burn", "future_grant")]
    assert sorted(grant_titles) == expected_titles

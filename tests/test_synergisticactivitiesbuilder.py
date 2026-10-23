import os
import subprocess
from pathlib import Path

import pytest

from regolith.builders.synergisticactivitiesbuilder import activity_years, select_activities

PERSON = {
    "_id": "me",
    "name": "Me Myself",
    "service": [
        {"name": "Board", "uuid": "aaaa1111-0000"},
        {"name": "Committee", "uuid": "aaaa2222-0000"},
        {"name": "No uuid"},
    ],
    "software": [{"name": "A package", "uuid": "bbbb1111-0000"}],
}


@pytest.mark.parametrize(
    "uuid_fragments, expected_names, expected_problems",
    [
        # Test choosing activities by uuid from any of a person's lists
        # C1: full and partial uuids from two lists, expect the entries in the order given
        (["bbbb", "aaaa2222-0000", "aaaa1"], ["A package", "Committee", "Board"], []),
        # C2: 1. a uuid matching nothing, 2. one matching two entries, expect both reported
        # and the others still chosen
        (["zzzz", "aaaa", "bbbb"], ["A package"], ["zzzz matches no entry", "aaaa matches 2 entries"]),
    ],
)
def test_select_activities(uuid_fragments, expected_names, expected_problems):
    actual_activities, actual_problems = select_activities(PERSON, uuid_fragments)
    assert [activity["name"] for activity in actual_activities] == expected_names
    assert actual_problems == expected_problems


@pytest.mark.parametrize(
    "entry, expected_years",
    [
        # Test the years shown for an activity
        # C1: a begin and end in different years, expect a range
        ({"begin_date": "2018-01-01", "end_date": "2021-06-30"}, "2018--2021"),
        # C2: no end, expect it to run to the present
        ({"begin_date": "2019-01-01"}, "2019--present"),
        # C3: a single date, expect one year
        ({"year": 2020, "month": 3}, "2020"),
        # C4: no dates, expect nothing
        ({}, ""),
    ],
)
def test_activity_years(entry, expected_years):
    assert activity_years(entry) == expected_years


def test_build_synergistic_activities(make_db):
    # Test that the activities chosen by uuid are written in the order given
    os.chdir(make_db)
    subprocess.run(
        [
            "regolith",
            "build",
            "synergistic-activities",
            "--no-pdf",
            "--people",
            "scopatz",
            "--kwargs",
            "uuid:c4e7",
            "uuid:8a1d",
        ],
        check=True,
    )
    tex = (Path(make_db) / "_build" / "synergistic-activities" / "scopatz-synergistic-activities.tex").read_text()
    actual_items = [line for line in tex.splitlines() if line.startswith(r"\item")]
    expected_items = [
        r"\item \textbf{Co-editor, Journal of Nuclear Software} (2019--present). "
        "Handle about 40 manuscripts a year on fuel cycle simulation.",
        r"\item \textbf{National Steering Committee} (2018--2021).",
    ]
    assert actual_items == expected_items

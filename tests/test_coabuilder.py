import datetime as dt
import os
import subprocess
from pathlib import Path

import openpyxl
import pytest

from regolith.builders.coabuilder import get_editorial_board_collaborators

PEOPLE = [{"_id": "chief", "name": "Ann Chief", "aka": ["A. Chief"]}]
CONTACTS = [
    {"_id": "coed", "name": "Bob Coeditor", "aka": []},
    {"_id": "plain", "name": "Cy Member", "aka": []},
]
MEMBERS = [
    {"id": "chief", "role": "editor-in-chief"},
    {"id": "Bob Coeditor", "role": "co-editor"},
    {"id": "plain", "role": "member"},
]
SINCE_DATE = dt.date(2024, 10, 22)
UNTIL_DATE = dt.date(2026, 10, 22)


def board_service(role, members=MEMBERS, **dates):
    return {
        "name": "Editor, Journal X",
        "type": "profession",
        "editorial_board": {"journal": "Journal X", "role": role, "members": members},
        **dates,
    }


@pytest.mark.parametrize(
    "service, expected_editors, expected_missing",
    [
        # Test which editorial board members a person lists in table 5 of the NSF form
        (
            # C1: a co-editor on a current board, expect the editor-in-chief and the other
            # co-editor, found in people or contacts by id or name, last active on the form date
            [board_service("co-editor", begin_date="2019-01-01")],
            [
                ("chief", "editor-in-chief", "Journal X", UNTIL_DATE),
                ("coed", "co-editor", "Journal X", UNTIL_DATE),
            ],
            [],
        ),
        (
            # C2: the editor-in-chief, expect the whole board, plain members included
            [board_service("editor-in-chief", begin_date="2019-01-01")],
            [
                ("chief", "editor-in-chief", "Journal X", UNTIL_DATE),
                ("coed", "co-editor", "Journal X", UNTIL_DATE),
                ("plain", "member", "Journal X", UNTIL_DATE),
            ],
            [],
        ),
        (
            # C3: a board left within the window, expect its members last active on the end date
            [board_service("co-editor", begin_date="2019-01-01", end_date="2025-06-30")],
            [
                ("chief", "editor-in-chief", "Journal X", dt.date(2025, 6, 30)),
                ("coed", "co-editor", "Journal X", dt.date(2025, 6, 30)),
            ],
            [],
        ),
        (
            # C4: 1. a board left before the window, 2. service that is not a board,
            # expect no one
            [
                board_service("co-editor", begin_date="2019-01-01", end_date="2023-12-31"),
                {"name": "Steering committee", "type": "profession", "year": 2026},
            ],
            [],
            [],
        ),
        (
            # C5: a member in neither people nor contacts, expect them reported with the
            # journal and the others still listed
            [
                board_service(
                    "co-editor",
                    members=[{"id": "ghost", "role": "co-editor"}, {"id": "chief", "role": "editor-in-chief"}],
                    begin_date="2019-01-01",
                )
            ],
            [("chief", "editor-in-chief", "Journal X", UNTIL_DATE)],
            ["ghost (Journal X)"],
        ),
    ],
)
def test_get_editorial_board_collaborators(service, expected_editors, expected_missing):
    person = {"_id": "me", "name": "Me Myself", "service": service}
    actual_editors, actual_missing = get_editorial_board_collaborators(
        person, PEOPLE, CONTACTS, SINCE_DATE, UNTIL_DATE
    )
    actual_editors = [
        (editor["person"]["_id"], editor["type"], editor["journal"], editor["interaction_date"])
        for editor in actual_editors
    ]
    assert actual_editors == expected_editors
    assert actual_missing == expected_missing


def test_editorial_boards_fill_table_5(make_db):
    # Test that the editorial board in scopatz's service fills table 5 of the NSF form
    os.chdir(make_db)
    subprocess.run(["regolith", "build", "recent-collabs", "--no-pdf", "--people", "scopatz"], check=True)
    sheet = openpyxl.load_workbook(Path(make_db) / "_build" / "recent-collabs" / "scopatz_nsf.xlsx").worksheets[0]
    actual_rows = [[sheet[f"{column}{row}"].value for column in "ABCD"] for row in (64, 65)]
    expected_rows = [
        ["B:", "Billinge, Simon", "The University of South Carolina", "Journal of Nuclear Software"],
        ["E:", "Friend, Anthony", "Columbia University", "Journal of Nuclear Software"],
    ]
    assert actual_rows == expected_rows

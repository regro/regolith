"""Classlist implementation."""

import csv
import json
import os
import re
import sys
from html.parser import HTMLParser
from pprint import pformat, pprint

from nameparser import HumanName


def load_json(filename):
    """Returns students as a list of dicts from JSON file."""
    with open(filename, encoding="utf-8") as f:
        students = json.load(f)
    return students


def load_csv(filename, format="columbia"):
    """Returns students as a list of dicts from a csv from Columbia
    Courseworks."""
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        students = []
        for row in reader:
            students.append(row)

    if format == "columbia":
        email_suffix = "@columbia.edu"
        [
            stud.update(
                {
                    "first_name": HumanName(stud["Student"]).first,
                    "last_name": HumanName(stud["Student"]).last,
                    "email": f"{stud.get('SIS User ID').strip()}{email_suffix}",
                    "university_id": stud.get("SIS User ID"),
                }
            )
            for stud in students
        ]

    for student in students:
        student["first_name"] = student.get("first_name").strip()
        student["last_name"] = student.get("last_name").strip()
        student["_id"] = "{} {}".format(student.get("first_name"), student.get("last_name")).strip()
        student["email"] = student.get("email").strip()
        student["university_id"] = student["university_id"].strip()

    return students


RE_ID = re.compile(r"^[A-Z]\d+$")
RE_NAME = re.compile("^[A-Za-z-]+$")


def _check_name(name, label, full):
    parts = (name[:-1] if name.endswith(".") else name).split()
    for part in parts:
        if RE_NAME.match(part) is None:
            print("skipping because of {} name: {}".format(label, full))
            return False
    return True


class UscHtmlParser(HTMLParser):
    """Class for parsing data from USC-formatted HTML."""

    def __init__(self):
        super().__init__()
        self.student = None
        self.students = []
        self.intable = self.inrow = self.incol = False

    def should_handle(self):
        return self.intable or self.inrow or self.incol

    def handle_starttag(self, tag, attrs):
        if tag == "table":  # we don't support nesting tables
            self.intable = True
        if not self.should_handle():
            return
        elif tag == "tr":
            self.inrow = True
            self.student = {}
        elif tag == "td":
            self.incol = True
        elif tag == "a" and self.incol:
            for attr, val in attrs:
                if attr == "href" and val.startswith("mailto:"):
                    _, _, email = val.partition(":")
                    self.student["email"] = email
                    break

    def handle_endtag(self, tag):
        if not self.should_handle():
            return
        if tag == "table":
            self.intable = False
        elif tag == "tr":
            if len(self.student) > 0 and "_id" in self.student:
                self.students.append(self.student)
            self.student = None
            self.inrow = False
        elif tag == "td":
            self.incol = False

    def handle_data(self, data):
        if not self.incol:
            return
        if "," in data:
            # found name
            last, _, first = data.partition(",")
            first = first.strip()
            last = last.strip()
            if not _check_name(first, "first", data):
                return
            if not _check_name(last, "last", data):
                return
            self.student["_id"] = first + " " + last
        elif RE_ID.match(data) is not None:
            self.student["university_id"] = data


def load_usc(filename):
    """Returns students as a list of dicts from an HTML file obtainted
    from the University of South Carolina."""
    with open(filename, encoding="utf-8") as f:
        html = f.read()
    parser = UscHtmlParser()
    parser.feed(html)
    return parser.students


LOADERS = {"usc": load_usc, "json": load_json, "csv": load_csv}


def add_students_to_db(students, rc):
    """Add new students to the student directory."""
    for student in students:
        rc.client.update_one(rc.db, "students", {"_id": student["_id"]}, student, upsert=True)


def add_students_to_course(students, rc):
    """Add students to the course listed."""
    course = rc.client.find_one(rc.db, "courses", {"_id": rc.course_id})
    if not course:
        raise ValueError(f"no course {rc.course_id} found in database")
    registry = {s["_id"] for s in students}
    if rc.op == "add":
        registry |= set(course["students"])
    elif rc.op == "replace":
        pass
    else:
        raise ValueError("operation {0!r} nor recognized".format(rc.op))
    course["students"] = sorted(registry)
    rc.client.update_one(rc.db, "courses", {"_id": rc.course_id}, course, upsert=True)


def register(rc):
    """Entry point for registering classes."""
    if not os.path.exists(rc.filename):
        sys.exit(
            "classlist file {} can't be found\nPlease check the filename " "and try again".format(rc.filename)
        )
    if rc.format is None:
        rc.format = os.path.splitext(rc.filename)[1][1:]
    loader = LOADERS[rc.format]
    students = loader(rc.filename)
    if rc.dry_run:
        pprint(students)
        return
    if rc.db is None:
        dbs = rc.client.keys()
        if len(dbs) == 1:
            rc.db = list(dbs)[0]
        else:
            raise RuntimeError(
                "More than one database present in run control, "
                'please select one with the "--db" option. '
                "Available dbs are: " + pformat(dbs)
            )
    add_students_to_db(students, rc)
    add_students_to_course(students, rc)

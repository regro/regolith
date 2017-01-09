"""Classlist implementation"""
import os
import re
import json
from html.parser import HTMLParser


def load_json(filename):
    """Returns students as a list of dicts from JSON file."""
    with open(filename) as f:
        students = json.load(f)
    return students


RE_ID = re.compile('[A-Z]\d+')
RE_NAME = re.compile('[A-Za-z]+')


class UscHtmlParser(HTMLParser):
    """Class for parsing data from USC-formatted HTML."""

    def __init__(self):
        super().__init__()
        self.student = None
        self.students = []
        self.intable = self.inrow = self.incol = False

    def should_handle(self):
        return (self.intable or self.inrow or self.incol)

    def handle_starttag(self, tag, attrs):
        if not self.should_handle():
            return
        if tag == 'table':  # we don't support nesting tables
            self.intable = True
        elif tag == 'tr':
            self.inrow = True
            self.student = {}
        elif tag == 'td':
            self.incol = True
        elif tag == 'a' and self.incol:
            for attr, val in attrs:
                if attr == 'href' and val.startswith('mailto:'):
                    _, _, email = val.partition(':')
                    self.student['email'] = email
                    break

    def handle_endtag(self, tag):
        if not self.should_handle():
            return
        if tag == 'table':
            self.intable = False
        elif tag == 'tr':
            if len(self.student) > 0:
                self.students.append(self.student)
            self.student = None
            self.inrow = False
        elif tag == 'td':
            self.incol = False

    def handle_data(self, data):
        if not self.incol:
            return
        if ',' in data:
            # found name
            last, first = data.partition(',')
            if RE_NAME.match(first) is None:
                return
            if RE_NAME.match(last[:-1] if last.endswith('.') else last) is None:
                return
            self.student['_id'] = first.strip() + ' ' + last.strip()
        elif RE_ID.match(data) is not None:
            self.student['university_id'] = data


def load_usc(filename):
    """Returns students as a list of dicts from an HTML file obtainted from the University of
    South Carolina.
    """
    with open(filename) as f:
        html = f.read()
    parser = UscHtmlParser()
    parser.feed(html)
    return parser.students


LOADERS = {
    'usc': load_usc,
    'json': load_json,
    }


def add_students_to_db(students, rc):
    """Add new students to the student directory."""
    for student in students:
        rc.client.update_one(rc.db, 'students', {'_id': student['_id']},
                             {'$set': student}, upsert=True)


def add_students_to_course(students, rc):
    """Add students to the course listed"""
    course = rc.client.find_one(rc.db, 'courses', {'_id': rc.course_id})
    registry = set(course['students']) | {s['_id'] for s in students}
    course['students'] = sorted(registry)
    rc.client.update_one(rc.db, 'courses', {'_id': rc.course_id},
                         {'$set': course}, upsert=True)


def register(rc):
    """Entry point for registering classes."""
    if rc.format is None:
        rc.format = os.path.splitext(rc.filename)[1][1:]
    loader = LOADERS[rc.format]
    students = loader(rc.filename)
    add_students_to_db(students, rc)
    add_students_to_course(students, rc)

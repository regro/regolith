"""Emails people via SMTP."""

import os
import smtplib
import tempfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from docutils.core import publish_string
except ImportError:
    publish_string

from regolith.builders.gradebuilder import GradeReportBuilder
from regolith.tools import all_docs_from_collection


def attach_txt(filename):
    with open(filename, "r", encoding="utf-8") as f:
        txt = f.read()
    msg = MIMEText(txt, _subtype="text")
    return msg


def attach_pdf(filename):
    with open(filename, "rb", encoding="utf-8") as f:
        pdf = f.read()
    msg = MIMEApplication(pdf, _subtype="pdf")
    return msg


ATTACHERS = {
    ".txt": attach_txt,
    ".rst": attach_txt,
    ".pdf": attach_pdf,
    ".ipynb": attach_txt,
}


def make_message(rc, to, subject="", body="", attachments=()):
    """Creates an email following the appropriate format.

    The body kwarg may be a string of restructured text.  Attachments is
    a list of filenames to attach.
    """
    msg = MIMEMultipart("alternative")
    plain = MIMEText(body, "plain")
    msg.attach(plain)
    if publish_string is not None:
        html = publish_string(
            body,
            writer_name="html",
            settings_overrides={"output_encoding": "unicode"},
        )
        html = MIMEText(html, "html")
        msg.attach(html)
    if attachments:
        text = msg
        msg = MIMEMultipart("mixed")
        msg.attach(text)
        for attachment in attachments:
            _, ext = os.path.splitext(attachment)
            att = ATTACHERS[ext](attachment)
            att.add_header(
                "content-disposition",
                "attachment",
                filename=os.path.basename(attachment),
            )
            msg.attach(att)
    msg["Subject"] = subject
    msg["From"] = rc.email["from"]
    msg["To"] = to
    return (to, msg.as_string())


def test_email(rc):
    """Sends a test email from regolith."""
    if rc.to is None:
        raise ValueError("--to must be given to send a test email.")
    with tempfile.NamedTemporaryFile(suffix=".rst", delete=False) as f:
        f.write(b"This is *only* a test attachment.\n")
        f.flush()
        message = make_message(
            rc,
            rc.to,
            subject="Regolith test email",
            body="This is *only* a test. Do not be alarmed.",
            attachments=[f.name],
        )
    return [message]


def grade_email(rc):
    """Sends grade report emails to students."""
    gradedir = os.path.join(rc.builddir, GradeReportBuilder.btype)
    addresses = {x["_id"]: x["email"] for x in list(all_docs_from_collection(rc.client, "students"))}
    messages = []
    for course in all_docs_from_collection(rc.client, "courses"):
        if not course.get("active", True):
            continue
        course_id = course["_id"]
        if course_id not in rc.course_ids:
            continue
        for student_id in course["students"]:
            base = GradeReportBuilder.basename(student_id, course_id) + ".pdf"
            fname = os.path.join(gradedir, base)
            if not os.path.isfile(fname):
                raise RuntimeError(
                    fname + " does not exist, please run " '"regolith build grade" prior to emailing ' "grades."
                )
            message = make_message(
                rc,
                addresses[student_id],
                subject="Current grades for " + course_id,
                body="Please see the attached PDF and " "please report any errors.",
                attachments=[fname],
            )
            messages.append(message)
    return messages


def class_email(rc):
    """Sends an email to all students in the active classes."""
    addresses = {x["_id"]: x["email"] for x in list(all_docs_from_collection(rc.client, "students"))}
    messages = []
    for course in all_docs_from_collection(rc.client, "courses"):
        if not course.get("active", True):
            continue
        course_id = course["_id"]
        if course_id not in rc.course_ids:
            continue
        subject = "[{0}] {1}".format(course_id, rc.subject)
        for student_id in course["students"]:
            message = make_message(
                rc,
                addresses[student_id],
                subject=subject,
                body=rc.body,
                attachments=rc.attachments,
            )
            messages.append(message)
    return messages


def list_email(rc):
    """List class emails."""
    course = rc.client.find_one(rc.db, "courses", {"_id": rc.course_ids})
    student_ids = set(course["students"])
    students = rc.client[rc.db]["students"]
    emails = [s["email"] for s in students.values() if s["_id"] in student_ids]
    print(",".join(sorted(emails)))


EMAIL_CONSTRUCTORS = {
    "test": test_email,
    "grade": grade_email,
    "grades": grade_email,
    "class": class_email,
    "list": list_email,
}


def emailer(rc):
    """Constructs and sends out emails."""
    constructor = EMAIL_CONSTRUCTORS[rc.email_target]
    emails = constructor(rc)
    if emails is None:
        return
    conf = rc.email
    with smtplib.SMTP(conf["url"], port=conf["port"]) as smtp:
        smtp.set_debuglevel(conf["verbosity"])
        if conf["tls"]:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(conf["user"], conf["password"])
        for to, message in emails:
            print("sending email to " + to + "...")
            smtp.sendmail(conf["from"], to, message)

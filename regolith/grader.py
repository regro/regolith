"""Flask app for grading regolith."""
import json
import traceback

from flask import Flask, abort, request, render_template, redirect, url_for

app = Flask("regolith")


@app.route("/", methods=["GET", "POST"])
def root():
    rc = app.rc
    status = None
    if request.method == "POST":
        form = request.form
        if "shutdown" in form:
            return shutdown()
        if "rowdata" in form:
            grade = form_to_grade_row(form)
        else:
            grade = form_to_grade_assignment(form)
        insert_grade(grade, form, rc)
        status = "submitted {0} ✓".format(grade["_id"])
        return status
    return render_template(
        "grader.html",
        json=json,
        rc=rc,
        str=str,
        status=status,
        range=range,
        len=len,
        sorted=sorted,
        enumerate=enumerate,
        by_id=lambda x: x["_id"],
    )


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown", methods=["GET", "POST"])
def shutdown():
    shutdown_server()
    return "Regolith server shutting down...\n"


def form_to_grade_assignment(form):
    """Creates a grade dict from an assignment form."""
    grade_id = "{student}-{assignment}-{course}".format(**form)
    grade = {
        "_id": grade_id,
        "student": form["student"],
        "assignment": form["assignment"],
        "course": form["course"],
    }
    if form["filename"]:
        grade["filename"] = form["filename"]
    scores = {
        int(k[5:]): float(v) for k, v in form.items() if k.startswith("score")
    }
    scores = sorted(scores.items())
    grade["scores"] = [v for _, v in scores]
    return grade


def form_to_grade_row(form):
    """Creates a grade dict from a row form."""
    course = form["course"]
    student = form["student"]
    assignment, _, _ = form["assignment"].partition("[")
    rowdata = json.loads(form["rowdata"])
    grade = {"student": student, "assignment": assignment, "course": course}
    grade["_id"] = "{student}-{assignment}-{course}".format(**grade)
    scores = {}
    for k, v in rowdata.items():
        if not k.startswith(assignment):
            continue
        _, _, n = k.partition("[")
        n, _, _ = n.partition("]")
        scores[int(n)] = v
    scores = sorted(scores.items())
    grade["scores"] = [v for _, v in scores]
    return grade


def insert_grade(grade, form, rc):
    """Inserts a grade into the database."""
    dbname = form["dbname"]
    collname = "grades"
    try:
        coll = rc.client[dbname][collname]
    except (KeyError, AttributeError):
        abort(404)
    try:
        added = rc.client.insert_one(dbname, collname, grade)
    except Exception:
        traceback.print_exc()
        raise

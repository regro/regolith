"""Flask app for looking at information in regolith."""
import json
import traceback
import tempfile
import os

from flask import Flask, abort, request, render_template, redirect, url_for

from regolith.schemas import validate
from regolith.chained_db import _convert_to_dict


app = Flask("regolith")


@app.route("/", methods=["GET", "POST"])
def root():
    rc = app.rc
    if request.method == "POST":
        form = request.form
        return redirect("/db/{dbname}/coll/{collname}".format(**form))
    return render_template("index.html", rc=rc)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown", methods=["GET", "POST"])
def shutdown():
    shutdown_server()
    return "Regolith server shutting down...\n"


@app.route("/db/<dbname>/coll/<collname>", methods=["GET", "POST"])
def collection_page(dbname, collname):
    rc = app.rc
    try:
        coll = rc.client[dbname][collname]
    except (KeyError, AttributeError):
        abort(404)
    status = status_id = None
    if request.method == "POST":
        form = request.form
        if "shutdown" in form:
            return shutdown()
        elif "cancel" in form:
            body = json.loads(form["body"].strip())
            status = "canceled"
            status_id = str(body["_id"])
        elif "save" in form:
            try:
                body = json.loads(form["body"].strip())
            except Exception:
                td = tempfile.TemporaryDirectory()
                n = os.path.join(td.name, "regolith.txt")
                print(
                    "Error in json parsing writing text file to {}. "
                    "Please try again.".format(n)
                )
                with open(n, "w", encoding='utf-8') as f:
                    f.write(form["body"])
                traceback.print_exc()
                raise
            tv, errors = validate(dbname, body, rc.schemas)
            if not tv:
                td = tempfile.TemporaryDirectory()
                n = os.path.join(td.name, "regolith.txt")
                with open(n, "w", encoding='utf-8') as f:
                    f.write(form["body"])
                raise ValueError(
                    "Error while validating the record,"
                    " writing text file to {}. "
                    "Please try again.\n\n"
                    "Your errors were\n"
                    "------------------"
                    "{}".format(n, errors)
                )

            rc.client.update_one(dbname, collname, {"_id": body["_id"]}, body)
            status = "saved ✓"
            status_id = str(body["_id"])
        elif "add" in form:
            try:
                body = json.loads(form["body"].strip())
                print(body)
            except Exception:
                td = tempfile.TemporaryDirectory()
                n = os.path.join(td.name, "regolith.txt")
                print(
                    "Error in json parsing writing text file to {}. "
                    "Please try again.".format(n)
                )
                with open(n, encoding='utf-8') as f:
                    f.write(form["body"])
                traceback.print_exc()
                raise
            tv, errors = validate(dbname, body, rc.schemas)
            if not tv:
                td = tempfile.TemporaryDirectory()
                n = os.path.join(td.name, "regolith.txt")
                with open(n, encoding='utf-8') as f:
                    f.write(form["body"])
                raise ValueError(
                    "Error while validating the record,"
                    " writing text file to {}. "
                    "Please try again.\n\n"
                    "Your errors were\n"
                    "------------------"
                    "{}".format(n, errors)
                )
            try:
                added = rc.client.insert_one(dbname, collname, body)
            except Exception:
                traceback.print_exc()
                raise
            status = "added ✓"
            status_id = str(body["_id"])
        elif "delete" in form:
            body = json.loads(form["body"].strip())
            deled = rc.client.delete_one(dbname, collname, body)
    return render_template(
        "collection.html",
        rc=rc,
        dbname=dbname,
        len=len,
        str=str,
        status=status,
        status_id=status_id,
        collname=collname,
        coll=coll,
        json=json,
        min=min,
        conv=_convert_to_dict,
    )

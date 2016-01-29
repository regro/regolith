"""Flask app for grading regolith."""
import traceback

from flask import Flask, abort, request, render_template, redirect, url_for
from bson import json_util, objectid

from regolith.tools import insert_one, delete_one

app = Flask('regolith')


@app.route('/', methods=['GET', 'POST'])
def root():
    rc = app.rc
    if request.method == 'POST':
        form = request.form
    return render_template('grader.html', rc=rc)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    shutdown_server()
    return 'Regolith server shutting down...\n'



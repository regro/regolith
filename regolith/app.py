"""Flask app for looking at information in regolith."""
from flask import Flask, request, render_template
from werkzeug.exceptions import abort
from bson import json_util

app = Flask('regolith')


@app.route('/')
def root():
    rc = app.rc
    return render_template('index.html', rc=rc)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    shutdown_server()
    return 'Regolith server shutting down...\n'


@app.route('/db/<dbname>/coll/<collname>', methods=['GET', 'POST'])
def collection_page(dbname, collname):
    rc = app.rc
    try:
        coll = rc.client[dbname][collname]
    except (KeyError, AttributeError):
        abort(404)
    status = status_id = None
    if request.method == 'POST':
        form = request.form
        if 'shutdown' in form:
            return shutdown()
        elif 'cancel' in form:
            body = json_util.loads(form['body'])
            status = 'canceled'
            status_id = str(body['_id'])
        elif 'save' in form:
            body = json_util.loads(form['body'])
            coll.save(body) 
            status = 'saved ✓'
            status_id = str(body['_id'])
    return render_template('collection.html', rc=rc, dbname=dbname, len=len,
                           status=status, status_id=status_id, str=str,
                           collname=collname, coll=coll, json_util=json_util)

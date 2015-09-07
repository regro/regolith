"""Flask app for looking at information in regolith."""
from flask import Flask, abort, request, render_template, redirect, url_for
from bson import json_util, objectid

from regolith.tools import insert_one, delete_one

app = Flask('regolith')


@app.route('/', methods=['GET', 'POST'])
def root():
    rc = app.rc
    if request.method == 'POST':
        form = request.form
        return redirect('/db/{dbname}/coll/{collname}'.format(**form))
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
            body = json_util.loads(form['body'].strip())
            status = 'canceled'
            status_id = str(body['_id'])
        elif 'save' in form:
            body = json_util.loads(form['body'].strip())
            coll.save(body) 
            status = 'saved ✓'
            status_id = str(body['_id'])
        elif 'add' in form:
            body = json_util.loads(form['body'].strip())
            added = insert_one(coll, body)
            status = 'added ✓'
            status_id = str(added.inserted_id)
        elif 'delete' in form:
            body = json_util.loads(form['body'].strip())
            deled = delete_one(coll, body)
    return render_template('collection.html', rc=rc, dbname=dbname, len=len, str=str,
                           status=status, status_id=status_id, objectid=objectid,
                           collname=collname, coll=coll, json_util=json_util)

"""Flask app for looking at information in regolith."""
from flask import Flask, request, render_template
from werkzeug.exceptions import abort

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


@app.route('/db/<dbname>/coll/<collname>')
def collection_page(dbname, collname):
    rc = app.rc
    try:
        coll = rc.client[dbname][collname]
    except (KeyError, AttributeError):
        abort(404)
    return render_template('collection.html', rc=rc, dbname=dbname, 
                           collname=collname, coll=coll)

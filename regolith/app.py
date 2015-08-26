"""Flask app for looking at information in regolith."""
from flask import Flask, request

app = Flask('regolith')


@app.route('/')
def root():
    return 'Welcome to Regolith'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    shutdown_server()
    return 'Regolith server shutting down...'

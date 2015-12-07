from flask import Flask
from flask import request
from flask import abort

import requests

app = Flask(__name__)

_key = None
_client_ips = None
_max_requests = None
_count = 0


@app.route('/')
def get_shared_secret():
    global _count, _max_requests, _client_ips
    if _client_ips:
        if request.remote_addr not in _client_ips:
            abort(403)
    _count += 1
    if _max_requests is not None:
        if _count >= _max_requests:
            shutdown_server()
    return _key


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def start_server(share_key, max_requests = None, valid_ips = None):
    global _key, _client_ips, _max_requests
    _key = share_key
    _client_ips = valid_ips
    _max_requests = max_requests
    app.run()


def get_sym_key(url):
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        return r.text
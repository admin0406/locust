import gevent
import json
import os.path
from gevent import wsgi
from stats import RequestStats

from core import hatch

from flask import Flask, make_response

app = Flask("Locust Monitor")
app.root_path = os.path.dirname(__file__)

_locust = None
_num_clients = None
_hatch_rate = None


@app.route("/")
def index():
    response = make_response(
        open(os.path.join(app.root_path, "static", "index.html")).read()
    )
    response.headers["Content-type"] = "text/html"
    return response


@app.route("/swarm")
def swarm():
    from core import locust_runner

    locust_runner.start_hatching()
    return {"message": "Swarming started"}


@app.route("/stats/requests")
def request_stats():
    stats = []

    for s in RequestStats.requests.itervalues():
        stats.append(
            [
                s.name,
                s.num_reqs,
                s.avg_response_time(),
                s.min_response_time(),
                s.max_response_time(),
                s.reqs_per_sec(),
            ]
        )

    return json.dumps(stats)


def start(locust, hatch_rate, num_clients):
    global _locust, _hatch_rate, _num_clients
    _locust = locust
    _hatch_rate = hatch_rate
    _num_clients = num_clients
    wsgi.WSGIServer(("", 8089), app).start()

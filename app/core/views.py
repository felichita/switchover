from sys import maxsize
import logging

import requests
from flask import Blueprint, Response
from json import dumps, loads
from ping3 import ping

from app.config import *
from app.utils import get_alive_nodes

load_dotenv(find_dotenv())
main = Blueprint('main', __name__)
redis_conn = REDIS_CONN
logger = logging.getLogger('Switchover Daemonset')


@main.route('/')
def index():
    return "It's a Switchover for patroni and kubernetes"


@main.route('/startup')
def startup_probe():
    """
    Startup probe for kubernetes. There is call the first mandatory liveness_probe.
    """
    liveness_probe()
    if redis_conn.get('cronjob_primary'):
        pass
    else:
        cronjob_primary = loads(discover_primary().data)['data']['node']
        logger.info(f'Set cronjob_primary={cronjob_primary}')
        if cronjob_primary is not None:
            redis_conn.set('cronjob_primary', cronjob_primary)
    primary_db_node = redis_conn.get('primary')  # We could take None, I know it
    for node in get_alive_nodes():
        if redis_conn.get(node):
            pass
        else:
            redis_conn.set(node, maxsize)  # Set oversize here, because we don't know what going on
    if primary_db_node is None:
        redis_conn.set('primary', 'fake')
    return "Startup probe, it's Switchover"


@main.route('/primary')
def discover_primary():
    res = RESPONSE
    for node in PATRONI_HOSTS:
        try:
            r = requests.get(f'{getenv("PATRONI_SCHEMA")}{node}:{getenv("PATRONI_PORT")}')
            if r.status_code == 200:
                logger.info(f"{node} is a primary node")
                res['data']['node'] = node
                res['message'] = 'successful'
                redis_conn.set('primary', node)
                return Response(dumps(res), status=200, mimetype='application/json')
            if r.status_code == 503:
                logger.info(f"{node} isn't primary")
        except Exception as e:
            logger.info(f'Error: {e}')
            res['error'] = 1
            res['message'] = f'Error: {e}'
            res['data']['node'] = None
    return Response(dumps(res), status=500, mimetype='application/json')


@main.route('/liveness')
def liveness_probe():
    """
    Liveness probe for kubernetes. There is set the ping of each alive node.
    """
    res = RESPONSE
    res['data']['node'] = NODE
    res['data']['round-trip'] = 999
    result_pings = []

    for _ in range(COUNT_PING):
        single_ping = ping(loads(discover_primary().data)['data']['node'], unit='ms')
        if single_ping:
            result_pings.append(single_ping)
            result_pings.sort()
    try:
        res['data']['round-trip'] = result_pings[round(0.5 * len(result_pings))]
        res['message'] = 'successful'
    except ZeroDivisionError:
        res['message'] = 'Something happened with ping'
    redis_conn.set(NODE, res['data']['round-trip'])
    return Response(dumps(res), status=200, mimetype='application/json')

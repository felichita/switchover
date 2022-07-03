import logging

from app.config import *
from app.utils import *

logger = logging.getLogger('Switchover Cronjob')
redis_conn = REDIS_CONN
sort_pings = []
check = dict()
alive_nodes = get_alive_nodes()

real_primary = redis_conn.get('primary').decode()
cronjob_primary = redis_conn.get('cronjob_primary').decode()

for node in alive_nodes:
    value = redis_conn.get(node)
    if value:
        check[node] = round(float(value.decode()))
        sort_pings.append(check[node])
        sort_pings.sort()

for node in alive_nodes:
    if check.get(node) <= sort_pings[percentile_number(25, alive_nodes)]:
        logger.info(f'Update_labels for {node} -> closely')
        update_labels(node, 'closely')
    elif check.get(node) <= sort_pings[percentile_number(75, alive_nodes)]:
        logger.info(f'Update_labels for {node} -> intermediate')
        update_labels(node, 'intermediate')
    else:
        logger.info(f'Update_labels for {node} -> far')
        update_labels(node, 'far')

if cronjob_primary != real_primary:
    for app in APPS:
        logger.info(f'kubectl rollout restart {app}')
        subprocess_wrapper(
            ['kubectl', 'rollout', 'restart', app]
        )
    logger.info(f'Change value for cronjob_primary -> {real_primary}')
    redis_conn.set('cronjob_primary', real_primary)

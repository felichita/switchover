from os import getenv
from itertools import filterfalse
import subprocess
from math import ceil

from kubernetes import client, config


api_instance = client.CoreV1Api()
config.load_incluster_config()
LABEL = getenv('LABEL')


def subprocess_wrapper(command):
    return subprocess.run(
        command, text=True, check=False,
        capture_output=True
    )


def percentile_number(percentile, node_list):
    return int(ceil(percentile/100 * len(node_list)) - 1)


def get_alive_nodes():
    alive_nodes = list()
    node_list = [item for item in api_instance.list_node().items]
    all_nodes = [item.metadata.name for item in node_list]
    for node in node_list:
        for conditions in node.status.conditions:
            if conditions.reason == 'KubeletReady' and conditions.type == 'Ready':
                alive_nodes.append(node.metadata.name)
    alive_nodes = [*filterfalse(lambda i: i in getenv('IGNORE_NODES').split(','), all_nodes)]
    return alive_nodes


def update_labels(node_name, distance):
    alive_nodes = get_alive_nodes()
    node_list = api_instance.list_node()
    body = {
        "metadata": {
            "labels": None
        }
    }
    for node in node_list.items:
        if node.metadata.name == node_name and node.metadata.name in alive_nodes:
            labels = node.metadata.labels
            labels[f'{LABEL}'] = distance
            body['metadata']['labels']= labels
    api_instance.patch_node(node_name, body)
    return body

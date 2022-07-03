from os import getenv

from dotenv import load_dotenv, find_dotenv
from kubernetes import config
import redis


load_dotenv(find_dotenv())
config.load_incluster_config()

NODE = getenv('NODE')
PATRONI_HOSTS = getenv('PATRONI_HOSTS').split(',')
APPS = getenv('APPS').split(',')
WINDOW_PING = int(getenv("WINDOW_PING"))
COUNT_PING = int(getenv('COUNT_PING'))
REDIS_CONN = redis.Redis(
    host=getenv('APP_REDIS_HOST'), port=int(getenv('APP_REDIS_PORT')), db=int(getenv('APP_REDIS_DB'))
)
LABEL = getenv('LABEL')

RESPONSE = {
    'error': 0,
    'message': None,
    'data': dict(),
}
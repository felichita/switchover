from os import getenv
from flask import Flask
from dotenv import load_dotenv, find_dotenv

from .core import main as main_blueprint

load_dotenv(find_dotenv())

switchover = Flask(__name__)


endpoints = (
    '',
)

# Register routes:
switchover.register_blueprint(main_blueprint)

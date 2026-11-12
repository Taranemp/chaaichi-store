
import os

from .base import *


SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ["ALLOWED_HOSTS"].split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
    if origin.strip()
]

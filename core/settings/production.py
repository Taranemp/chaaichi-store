
import os

import dj_database_url

from .base import *


SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ["ALLOWED_HOSTS"].split(",")
    if host.strip()
]

ALLOWED_HOSTS.append(".vercel.app")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
    if origin.strip()
]

DATABASES = {
    "default": dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=0,
        ssl_require=True,
    )
}

DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

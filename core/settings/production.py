from .base import *
from decouple import Config, RepositoryEnv

env = Config(RepositoryEnv(".production.env"))

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
DEBUG = True

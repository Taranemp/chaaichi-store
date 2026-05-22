from .base import *
from decouple import Config, RepositoryEnv

env = Config(RepositoryEnv(".development.env"))

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
DEBUG = True
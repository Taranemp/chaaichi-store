
from .base import *
from decouple import Config, RepositoryEnv

env = Config(RepositoryEnv(".development.env"))

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
DEBUG = True

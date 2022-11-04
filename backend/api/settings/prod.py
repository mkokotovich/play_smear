# flake8: noqa
import dj_database_url

from api.settings.common import *

DEBUG = False

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=False)

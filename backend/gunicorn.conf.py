import os

# gunicorn.conf.py
# Non logging stuff
bind = ":8000"
# Threads seem to break writing to neon.tech databases, for some reason
# For now, keeping database on fly.io
workers = 1
threads = 8

# Reload if source changes, but only when running locally
reload = bool(os.getenv("ENVIRON", "").lower() == "local")

# Access log - records incoming HTTP requests
accesslog = "-"
access_log_format = '%(h)s %(t)s "%(r)s" "%(a)s" %(r)s %(s)s %(b)s %(M)s ms %({x-request-id}o)s'

# Error log - records Gunicorn server goings-on
errorlog = "-"
# Whether to send Django output to the error log
capture_output = True
# How verbose the Gunicorn error logs should be
loglevel = "INFO"

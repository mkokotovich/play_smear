import os

# gunicorn.conf.py
# Non logging stuff
bind = ":8000"
workers = 2
threads = 4

# Reload if source changes, but only when running locally
reload = bool(os.getenv("ENVIRON", "").lower() == "local")

# Access log - records incoming HTTP requests
accesslog = "-"
access_log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s %(M)s ms'

# Error log - records Gunicorn server goings-on
errorlog = "-"
# Whether to send Django output to the error log
capture_output = True
# How verbose the Gunicorn error logs should be
loglevel = "INFO"

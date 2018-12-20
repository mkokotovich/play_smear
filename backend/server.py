from waitress import serve
from api.wsgi import application
serve(application, unix_socket='/tmp/nginx.socket', url_scheme='https')

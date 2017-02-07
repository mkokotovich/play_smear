from waitress import serve
from play_smear_api.play_smear_api import app
#serve(app, listen='0.0.0.0:5000', url_scheme='https')
serve(app, unix_socket='/tmp/nginx.socket', url_scheme='https')

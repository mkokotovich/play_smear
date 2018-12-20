from waitress import serve
from play_smear_api import app
app.debug = True
serve(app, listen='0.0.0.0:5000', url_scheme='https')

# play\_smear
Play the card game smear online

Angular2 front end
Python/Flask back end

To start servers in debug mode:
cd front\_end
ng serve

cd play\_smear\_api
python play\_smear\_api.py

This is deployed to heroku using nginx to serve the static files from angular2 front end, and nginx proxies the api calls to the backend through a unix socket.  

# play\_smear
Play the card game smear online
[![Build Status](https://travis-ci.org/mkokotovich/play_smear.svg?branch=master)](https://travis-ci.org/mkokotovich/play_smear)

Angular2 front end

Python/Flask back end

## To start debug servers:
### Front end
cd front\_end

ng serve

### Back End
cd play\_smear\_api
python play_smear_api.py

## To deploy for production
This is deployed to heroku using nginx to serve the static files from angular2 front end, and nginx proxies the api calls to the backend through a unix socket.  

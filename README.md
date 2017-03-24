[![Build Status](https://travis-ci.org/mkokotovich/play_smear.svg?branch=master)](https://travis-ci.org/mkokotovich/play_smear)
# play\_smear

Play the card game smear online:
http://www.playsmear.com

Angular2 front end

Python/Flask back end, using github.com/mkokotovich/pysmear for smear game logic.

## To start debug servers:
### Front end
cd front\_end

ng serve

### Back End
cd play\_smear\_api

python play_smear_api.py

## To deploy for production
This is deployed to heroku using nginx to serve the static files from angular2 front end, and nginx proxies the api calls to the backend through a unix socket.  

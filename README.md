# play\_smear
Play the card game smear online

Angular2 front end

Python/Flask back end

## To start debug servers:
### Front end
cd front\_end

ng serve

### Back End
cd play\_smear\_api
python debug\_server.py

## To deploy for production
This is deployed to heroku using nginx to serve the static files from angular2 front end, and nginx proxies the api calls to the backend through a unix socket.  

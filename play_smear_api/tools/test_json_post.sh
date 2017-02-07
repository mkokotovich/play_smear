#!/bin/bash
#curl -i -H "Content-Type: application/json" -X POST -d '{"numPlayers":"1", "username": "matt"}' http://localhost:5000/api/startgame/
curl -s -H "Content-Type: application/json" -X POST -d '{"numPlayers":"3", "username": "matt"}' http://localhost:5000/api/startgame/ | python -m json.tool

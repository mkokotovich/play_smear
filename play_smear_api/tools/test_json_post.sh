#!/bin/bash
set -xeuo pipefail
HOST="localhost:5000"
if [ $# -eq 1 ] ; then
    HOST=$1
fi
URL="http://${HOST}"
#curl -i -H "Content-Type: application/json" -X POST -d '{"numPlayers":"1"}' "${URL}/api/game/create/"
curl -s -H "Content-Type: application/json" -X POST -d '{"numPlayers":"3"}' "${URL}/api/game/create/" | python -m json.tool

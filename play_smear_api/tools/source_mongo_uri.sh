#!/bin/bash
export MONGODB_URI=$(heroku config --app playsmear | sed -ne 's/MONGODB_URI: \(.*\)/\1/p')

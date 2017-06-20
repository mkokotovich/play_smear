#!/bin/bash
export MONGODB_URI=$(heroku config | sed -ne 's/MONGODB_URI: \(.*\)/\1/p')

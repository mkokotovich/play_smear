#!/bin/sh
cd front_end
ng build --aot -prod
node server.js

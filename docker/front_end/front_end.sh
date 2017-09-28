#!/bin/bash
source /root/.bash_profile
nvm use v6.11.3
if [ ! -f /front_end_ready ] ; then
    echo "Setting up node for first run"
    cd /play_smear/front_end
    npm install
    npm install -g @angular/cli
    touch /front_end_ready
    echo "Node packages are installed"
fi

echo "Starting front end server"
cd /play_smear/front_end
ng serve --host 0.0.0.0 &> /play_smear/front_end.log

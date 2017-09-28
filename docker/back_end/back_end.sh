#!/bin/bash
if [ ! -f /back_end_ready ] ; then
    echo "Installing pip requirements"
    cd /play_smear
    pip install -r requirements.txt
    touch /back_end_ready
    echo "pip requirements installed"
fi

echo "Starting back end server"
cd /play_smear/play_smear_api
python play_smear_api.py &> /play_smear/back_end.log

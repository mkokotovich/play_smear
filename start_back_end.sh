#!/bin/sh
cd back_end
gunicorn --bind 0.0.0.0:5000 play_smear_api:app

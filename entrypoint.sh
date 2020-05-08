#!/bin/sh

exec gunicorn app:APP \
     -w 2 -t 120 \
     -b 0.0.0.0:$API_PORT \
     --max-requests 1000 \
     --log-level=info

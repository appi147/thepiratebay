#!/bin/bash

exec gunicorn app:APP \
     -w 2 -t 120 \
     -b 0.0.0.0:5000 \
     --max-requests 1000 \
     --log-level=info

#!/bin/bash

# Executes server using python2.7 (it has tornado installed)

PORT=$1
[ -z $1 ] && PORT=10001

rm *.pyc
echo "Running on port $PORT at $(hostname)" 
echo "  - Navigate to http://$(hostname):$PORT/" 
python2.7 server_test.py --port=$PORT

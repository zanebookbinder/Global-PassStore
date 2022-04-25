#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

KEYPAIR_PATH=$1

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/$USER-keypair $USER@${HOSTNAME} "pkill -u $USER -f '^python3 server.py 8012$'"
done

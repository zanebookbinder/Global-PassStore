#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

KEYPAIR_PATH=$1
USERNAME=$2

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH} ${USERNAME}@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && eval \`ssh-agent\` && ssh-add ~/.ssh/${USERNAME}-keypair && git pull && python3 server.py 8000"
done

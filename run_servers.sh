#!/bin/bash

HOSTS=$(python3 constants.py h)

IDX=0
for HOSTNAME in ${HOSTS} ; do 
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && git pull && python3 server.py &" &
    echo "server ${IDX} started: ${HOSTNAME}"
    let IDX=${IDX}+1
done

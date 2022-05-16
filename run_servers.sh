#!/bin/bash
# 1. connects to every server host
#   a. moves into Git repo directory for this project
#   b. pulls any updates to repo
#   c. execute python server code (actually starts the server -- port number in constants.py)

HOSTS=$(python3 constants.py h)

IDX=0
for HOSTNAME in ${HOSTS} ; do 
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && git pull && python3 server.py &" &
    echo "server ${IDX} started: ${HOSTNAME}"
    let IDX=${IDX}+1
done

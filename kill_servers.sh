#!/bin/bash

HOSTS=$(python3 constants.py h)
PORTNO=$(python3 constants.py p)

IDX=0
# iterating through every host and killing the server process for the current user
for HOSTNAME in ${HOSTS} ; do
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "pkill -u $USER -f '^python3 server.py$'"
    echo "server ${IDX} killed at port ${PORTNO}"
    let IDX=${IDX}+1
done
echo

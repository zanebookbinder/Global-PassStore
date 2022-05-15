#!/bin/bash

HOSTS=$(python3 constants.py h)

IDX=0
for HOSTNAME in ${HOSTS} ; do 
    # scp -i ~/.ssh/$USER-keypair ~/project-4---final-project-zane-danny-ahmed/server.py $USER@${HOSTNAME}:~/project-4---final-project-zane-danny-ahmed/server.py
    # ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && python3 server.py 8061 &" &
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && git pull && python3 server.py 8062 &" &
    echo "server ${IDX} started: ${HOSTNAME}"
    let IDX=${IDX}+1
done

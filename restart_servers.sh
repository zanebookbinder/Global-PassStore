#!/bin/bash
# 1. connect to every server host
#   a. kill all GPS server processes
#   b. moves into Git repo directory for this project
#   c. pulls any updates to repo
#   d. execute python server code (actually starts the server -- port number in constants.py)


HOSTS=$(python3 constants.py h)
PORTNO=$(python3 constants.py p)

IDX=0
for HOSTNAME in ${HOSTS} ; do
    # scp -i ~/.ssh/$USER-keypair ~/project-4---final-project-zane-danny-ahmed/server.py $USER@${HOSTNAME}:~/project-4---final-project-zane-danny-ahmed/server.py
    # ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "pkill -u $USER -f '^python3 server.py 8061$' && cd project-4---final-project-zane-danny-ahmed && python3 server.py 8061 &" &
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} "pkill -u $USER -f '^python3 server.py$' && cd project-4---final-project-zane-danny-ahmed && git pull && python3 server.py &" &
    echo "server ${IDX} restarted"
    let IDX=${IDX}+1
done
echo

#!/bin/bash

HOSTS=$(python3 constants.py h)

IDX=0
for HOSTNAME in ${HOSTS} ; do
    # scp [options] [source]:file [dest]:file
    # scp -i ~/.ssh/$USER/$USER-keypair ~/.ssh/$USER/$USER-keypair $USER@${HOSTNAME}:~/.ssh/$USER/$USER-keypair 
    ssh -i ~/.ssh/$USER-keypair $USER@${HOSTNAME} -o BatchMode=yes -o StrictHostKeyChecking=no "rm -rf project-4---final-project-zane-danny-ahmed && echo 'Host github.com' > .ssh/config && echo '    IdentityFile ~/.ssh/$USER-keypair' >> .ssh/config && echo '    StrictHostKeyChecking no' >> .ssh/config && chmod 600 .ssh/config && git clone git@github.com:bowdoin-dsys/project-4---final-project-zane-danny-ahmed.git"
    echo "Repo cloned on server ${IDX}"
    let IDX=${IDX}+1
done
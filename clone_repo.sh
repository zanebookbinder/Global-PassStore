#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

KEYPAIR_PATH=$1

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/$USER-keypair $USER@${HOSTNAME} "rm -rf project-4---final-project-zane-danny-ahmed && echo 'Host github.com' > .ssh/config && echo '    IdentityFile ~/.ssh/$USER-keypair' >> .ssh/config && echo '    StrictHostKeyChecking no' >> .ssh/config && chmod 600 .ssh/config && git clone git@github.com:bowdoin-dsys/project-4---final-project-zane-danny-ahmed.git"
done

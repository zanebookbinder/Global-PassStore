#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

USERNAME=$1
KEYPAIR_PATH=$2
FILE_TO_EXEC=$3

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "cd project-4---final-project-zane-danny-ahmed && git pull && python3 ${FILE_TO_EXEC} 8012 &" &
done

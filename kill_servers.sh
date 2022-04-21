#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

USERNAME=$1
KEYPAIR_PATH=$2
PROCESS_TO_KILL=$3
# could specify a port number variable for greater customizeability

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "pkill -u ${USERNAME} -f '^python3 ${PROCESS_TO_KILL} 8012$'"
done

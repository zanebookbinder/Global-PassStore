#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

KEYPAIR_PATH=$1
USERNAME=$2
PROCESS_TO_KILL=$3

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "jobs | grep project-4---final-project-zane-danny-ahmed/${PROCESS_TO_KILL} | while read -r line; do kill %$line[2]; done"
done

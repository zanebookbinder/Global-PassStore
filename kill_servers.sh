#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

KEYPAIR_PATH=$1
USERNAME=$2
PROCESS_TO_KILL=$3

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${KEYPAIR_PATH}/${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "ps -aux | grep -v grep | grep 'python3 ${PROCESS_TO_KILL} 8012' | grep ${USERNAME} | while read -r line; do stringarray=($line) kill $line[2]; done"
done

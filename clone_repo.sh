#!/bin/bash

HOSTS="52.90.4.149 54.236.244.145 54.211.164.149 54.205.63.8"

USERNAME=$1

for HOSTNAME in ${HOSTS} ; do
    ssh -i ${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "eval \`ssh-agent\` && ssh-add .ssh/${USERNAME}-keypair && git clone git@github.com:bowdoin-dsys/project-4---final-project-zane-danny-ahmed.git"
done

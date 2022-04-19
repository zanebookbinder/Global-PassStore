#!/bin/bash

#!/bin/bash

HOSTS="host1 host2 host3"
SCRIPT="pwd; ls"

USERNAME=$1


for HOSTNAME in ${HOSTS} ; do
    ssh -i ${USERNAME}-keypair ${USERNAME}@${HOSTNAME} "${SCRIPT}"
done
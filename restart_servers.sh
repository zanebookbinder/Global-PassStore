#!/bin/bash

KEYPAIR_PATH=$1

./kill_servers.sh "$1"
./run_servers.sh "$1"
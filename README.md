# Global PassStore (GPS) - A distributed password manager
## **Authors**:
#### Ahmed Hameed
#### Danny Little
#### Zane Bookbinder

<br/>

### *Version Date*: 5/16/2022

<br/>

GPS is a distributed password manager that splits user passwords into chunks and stores those pieces in various server nodes across the globe. This system is designed to be highly scalable, available, and fault-tolerant.

## **Program Files**
* client.py
* server.py
* constants.py
* testing.py
* utils.py
* clone_repo.sh - Copies the GPS program files, including client and server, onto the GPS server hosts. 
* run_servers.sh
* restart_servers.sh
* kill_servers.sh
* websites.txt
* dummyClient.py - irrelevant
* dummyServer.py - irrelevant

## **Program Instructions**
#### **First Time Setup**
1. Update all relevant constants in constants.py including:
    * server host IP addresses of GPS servers
    * node clusters
    * hosts to country mappings
    * port number for GPS server processes
2. Review and edit the clone_repo.sh file to ensure that various file paths and names are consistent with current system and coding environment.
3. Execute the clone_repo.sh bash script file to connect the various hosts and copy the GPS program onto those machines.
Terminal command example: "./clone_repo.sh"

<br/>

#### **Run GPS Servers**
To start the entire system by running the server code on all the server nodes:
1. Review and edit the run_servers.sh file to ensure that file paths and names are consistent with the current system and coding environment.
2. Execute the run_servers.sh file to start the GPS server.py process on every server node

<br/>

#### **Kill GPS Servers**
To kill the GPS server processes at every node in the system:
1. Review and edit the kill_servers.sh file to ensure that file paths and names are consistent with the current system and coding environment.
2. Execute the kill_servers.sh file to kill the GPS server.py process on every server node

<br/>

#### **Restart GPS Servers**
To kill the GPS server process and then execute the server code again at every server node:
1. Review and edit the restart_servers.sh file to ensure that file paths and names are consistent with the current system and coding environment.
2. Execute the restart_servers.sh file to kill and then restart the GPS server.py process on every server node


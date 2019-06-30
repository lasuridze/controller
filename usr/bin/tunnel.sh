#!/bin/bash

# it's usually a good idea to exit upon error
set -e

# your connection parameters
user=tunnel
server=139.162.185.135
remotePort=8889
localPort=8888

# some stuff autossh needs to know
AUTOSSH_SERVER_ALIVE_INTERVAL=30
AUTOSSH_SERVER_ALIVE_COUNT=2
export AUTOSSH_POLL=30
export AUTOSSH_GATETIME=0
export AUTOSSH_LOGFILE="/tmp/autossh.log"

# clean up log file on start
touch "${AUTOSSH_LOGFILE}"
rm "${AUTOSSH_LOGFILE}" || true

autossh  -N -M 0 \
  -o "ExitOnForwardFailure yes" \
  -o "ServerAliveInterval ${AUTOSSH_SERVER_ALIVE_INTERVAL}" \
  -o "ServerAliveCountMax ${AUTOSSH_SERVER_ALIVE_COUNT}" \
  -i /home/mihail/.ssh/id_rsa \
  -A ${user}@${server} \
  -R ${remotePort}:localhost:${localPort}

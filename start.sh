#!/bin/sh
# Start SSH in the background, then hand off to FRR's normal startup
/usr/sbin/sshd
exec /usr/lib/frr/docker-start

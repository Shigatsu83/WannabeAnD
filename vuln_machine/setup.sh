#!/bin/bash

# Generate random flags
USER_FLAG="user{$(openssl rand -hex 32)}"
ROOT_FLAG="root{$(openssl rand -hex 32)}"

# Write flags to files
echo "$USER_FLAG" > /home/ctf/user.txt
echo "$ROOT_FLAG" > /root/root.txt

# Set correct permissions
chown ctf:ctf /home/ctf/user.txt
chmod 644 /home/ctf/user.txt
chmod 600 /root/root.txt

# Start cron service (for flag rotation)
service cron start

#!/bin/bash

# Run initial setup (only once)
if [ ! -f "/home/ctf/flag_initialized" ]; then
    /setup.sh
    touch /home/ctf/flag_initialized
fi

# Start SSH service
service ssh start

# Start the Flask application in the background
python3 /var/www/app.py &

# Keep the container running and allow interactive SSH
#exec bash
tail -f /dev/null

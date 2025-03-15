#!/bin/bash

API_KEY="90ujr4e4r4kljk;jl2343"
TEAM_NAME=$(hostname)
SERVER_IP="http://192.168.100.7:8080"


# Fetch flag data
response=$(curl -s -X POST -d "api_key=$API_KEY&team=$TEAM_NAME" "$SERVER_IP/flag")
new_tick=$(echo "$response" | jq -r '.tick')
user_flag=$(echo "$response" | jq -r '.user_flag')
root_flag=$(echo "$response" | jq -r '.root_flag')

# Read the last tick from a file
LAST_TICK_FILE="/home/ctf_admin/last_tick.txt"
LAST_TICK=0
if [ -f "$LAST_TICK_FILE" ]; then
    LAST_TICK=$(cat "$LAST_TICK_FILE")
fi

# If the tick hasn't changed, retry after a short delay
if [ "$new_tick" -eq "$LAST_TICK" ]; then
    echo "[INFO] No flag update needed (same tick: $new_tick). Retrying in 3 seconds..."
    sleep 3
    response=$(curl -s -X POST -d "api_key=$API_KEY&team=$TEAM_NAME" "$SERVER_IP/flag")
    new_tick=$(echo "$response" | jq -r '.tick')
    user_flag=$(echo "$response" | jq -r '.user_flag')
    root_flag=$(echo "$response" | jq -r '.root_flag')
fi

# Update the flag only if tick is different
if [ "$new_tick" -ne "$LAST_TICK" ]; then
    echo "[INFO] Updating flags for tick $new_tick"
    echo "$new_tick" > "$LAST_TICK_FILE"

    # Write the user flag as the `ctf` user
    echo "$user_flag" | sudo -u ctf tee /home/ctf/user.txt > /dev/null

    # Write the root flag using `sudo`
    echo "$root_flag" | sudo tee /root/root.txt > /dev/null
else
    echo "[INFO] No flag update needed (tick unchanged: $new_tick)."
fi

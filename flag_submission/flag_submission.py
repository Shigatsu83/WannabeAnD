from flask import Flask, request, jsonify
import paramiko
import json

app = Flask(__name__)

# Store points for each team
team_scores = {
    "team1": 0,
    "team2": 0,
    "team3": 0,
    "team4": 0,
    "team5": 0
}

# SSH Credentials for accessing team machines
SSH_USERNAME = "ctfsystem"
SSH_PASSWORD = "myHardGuessedPw"
SSH_PORTS = {
    "team1": 11001,
    "team2": 11002,
    "team3": 11003,
    "team4": 11004,
    "team5": 11005
}

ADMIN_KEY = "supersecretadminkey"  # Change this for security

import paramiko

def get_flag_from_machine(team, flag_type):
    """Retrieve the correct flag from /home/ctf/user.txt or /root/root.txt via SSH."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using regular user "ctf"
        ssh.connect("192.168.100.7", port=SSH_PORTS[team], username=SSH_USERNAME, password=SSH_PASSWORD)

        # Use "sudo" to access the root flag
        flag_path = "/home/ctf/user.txt" if flag_type == "user" else "/root/root.txt"
        command = f"cat {flag_path}" if flag_type == "user" else f"sudo cat {flag_path}"

        stdin, stdout, stderr = ssh.exec_command(command)
        flag_value = stdout.read().decode().strip()

        ssh.close()
        return flag_value

    except Exception as e:
        return None


@app.route('/submit', methods=['POST'])
def submit_flag():
    """Handles flag submission and validation."""
    submitting_team = request.form.get("team")  # The team submitting the flag
    submitted_flag = request.form.get("flag")  # Flag submitted
    flag_type = request.form.get("type")  # 'user' or 'root'

    if submitting_team not in SSH_PORTS:
        return jsonify({"message": "Invalid team!", "status": "error"}), 400

    # Loop through all teams to find which team this flag belongs to
    for target_team in SSH_PORTS:
        if target_team == submitting_team:
            continue  # Skip checking the submitter's own flag

        real_flag = get_flag_from_machine(target_team, flag_type)
        if real_flag and submitted_flag == real_flag:
            # Assign points based on flag type
            points = 10 if flag_type == "user" else 50
            team_scores[submitting_team] += points  # Add points to the submitting team
            
            return jsonify({
                "message": f"Valid flag! {submitting_team} stole {flag_type} flag from {target_team} and earned {points} points.",
                "status": "success",
                "submitting_team": submitting_team,
                "target_team": target_team,
                "points_awarded": points,
                "total_score": team_scores[submitting_team]
            }), 200

    return jsonify({"message": "Invalid flag!", "status": "error"}), 400

@app.route('/scoreboard', methods=['GET'])
def scoreboard():
    """Returns the current scores of all teams."""
    return jsonify(team_scores), 200

@app.route('/debug_flags', methods=['GET'])
def debug_flags():
    """Retrieve current flags from all machines for debugging purposes (admin only)."""
    admin_key = request.args.get("admin_key")

    if admin_key != ADMIN_KEY:
        return jsonify({"message": "Unauthorized access!", "status": "error"}), 403

    flag_data = {}
    for team in SSH_PORTS:
        user_flag = get_flag_from_machine(team, "user")
        root_flag = get_flag_from_machine(team, "root")
        flag_data[team] = {
            "user_flag": user_flag,
            "root_flag": root_flag
        }

    return jsonify(flag_data), 200

@app.route('/test', methods=['GET'])
def test():
    return "TEST"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

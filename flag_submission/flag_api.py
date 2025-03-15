from flask import Flask, request, jsonify
import json
import os
import time
import traceback

app = Flask(__name__)

# Load API keys from environment variables
LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "default_local_key")
ADMIN_KEY = os.getenv("ADMIN_KEY", "my_super_admin_key")

# Ensure `flags.json` and `submitted_flags.json` are loaded from the correct directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FILE = os.path.join(BASE_DIR, "flags.json")
SUBMISSION_TRACKER = os.path.join(BASE_DIR, "submitted_flags.json")

# Example API keys (should be stored securely)
TEAM_API_KEYS = {
    "team1": "team1_secret_key",
    "team2": "team2_secret_key",
    "team3": "team3_secret_key"
}

def load_json(filename):
    """Load JSON data from a file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(filename, data):
    """Save JSON data to a file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_submissions():
    """Load submitted flags to track duplicate submissions."""
    return load_json(SUBMISSION_TRACKER)

def save_submissions(submissions):
    """Save the updated submission tracker."""
    save_json(SUBMISSION_TRACKER, submissions)


def load_flags():
    """Load flags from the JSON file and print debug output."""
    try:
        with open(FLAG_FILE, "r") as f:
            flags = json.load(f)
            print(f"[DEBUG] Loaded flags: {flags}")  # Debugging
            return flags
    except FileNotFoundError:
        print("[ERROR] flags.json file not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON Decode Error in flags.json: {e}")
        return {}


@app.route('/flag', methods=['POST'])
def get_flags():
    """Returns the current tick and flags for a specific team."""
    api_key = request.form.get("api_key")
    team = request.form.get("team")

    if not api_key or not team:
        return jsonify({"message": "Missing API key or team parameter", "status": "error"}), 400

    if api_key != LOCAL_API_KEY:
        return jsonify({"message": "Unauthorized access!", "status": "error"}), 403

    flags = load_flags()
    tick = flags.get("tick", 0)  # Default to 0 if tick is missing
    team_flags = flags["teams"]

    if team in team_flags:
        return jsonify({
            "tick": tick,
            "user_flag": team_flags[team]["user_flag"],
            "root_flag": team_flags[team]["root_flag"]
        })
    else:
        return jsonify({
            "tick": tick,
            "user_flag": "Not found",
            "root_flag": "Not found"
        })

@app.route('/submit', methods=['POST'])
def submit_flag():
    """Validates a submitted flag and ensures a team submits another team's flag."""
    try:
        api_key = request.form.get("api_key")
        submitted_flag = request.form.get("flag")

        if not api_key or not submitted_flag:
            return jsonify({"message": "Missing API key or flag", "status": "error"}), 400

        # Identify the team based on the API key
        submitting_team = next((t for t, key in TEAM_API_KEYS.items() if key == api_key), None)

        if not submitting_team:
            return jsonify({"message": "Invalid API key!", "status": "error"}), 403

        # Load flags
        flags = load_flags()

        # Check if `flags` is a dictionary
        if not isinstance(flags, dict):
            raise TypeError(f"Invalid flags format: Expected dict, got {type(flags)}")

        # Ensure `flags.json` contains "teams"
        if "teams" not in flags:
            raise KeyError("Missing 'teams' key in flags.json")

        teams_flags = flags["teams"]

        # Ensure that the submitting team is not checking its own flag
        for other_team, team_flags in teams_flags.items():
            if not isinstance(team_flags, dict):
                raise TypeError(f"Invalid flag structure for {other_team}: {team_flags}")

            if other_team != submitting_team:
                if submitted_flag == team_flags.get("user_flag"):
                    return jsonify({"message": f"User flag correct for {other_team}! +10 points", "status": "success"}), 200
                elif submitted_flag == team_flags.get("root_flag"):
                    return jsonify({"message": f"Root flag correct for {other_team}! +50 points", "status": "success"}), 200

        return jsonify({"message": "Invalid flag! You must submit another team's flag.", "status": "error"}), 400

    except Exception as e:
        error_trace = traceback.format_exc()
        app.logger.error(f"[ERROR] Exception in /submit endpoint: {e}\n{error_trace}")
        return jsonify({"message": "Internal Server Error", "error": str(e), "traceback": error_trace}), 500

@app.route('/flags/all', methods=['POST'])
def get_all_flags():
    """Returns all flags (admin access required) with error handling."""
    try:
        api_key = request.form.get("api_key")

        if not api_key:
            return jsonify({"message": "Missing API key", "status": "error"}), 400

        if api_key != ADMIN_KEY:
            return jsonify({"message": "Unauthorized access!", "status": "error"}), 403

        flags = load_flags()
        return jsonify(flags)

    except Exception as e:
        app.logger.error(f"[ERROR] Exception in /flags/all endpoint: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"message": "Internal Server Error", "status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

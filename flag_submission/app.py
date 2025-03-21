from flask import Flask, request, jsonify
import json
import os
import traceback
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://192.168.100.7"])

# Load API keys from environment variables
LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "default_local_key")
ADMIN_KEY = os.getenv("ADMIN_KEY", "my_super_admin_key")

# Ensure `flags.json` and `submitted_flags.json` are loaded from the correct directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONF_DIR = os.path.join(BASE_DIR, "config")
os.makedirs(DATA_DIR, exist_ok=True)


SCORE_FILE = os.path.join(DATA_DIR, "scores.json")
SUBMISSION_TRACKER = os.path.join(DATA_DIR, "submitted_flags.json")
FLAG_FILE = os.path.join(DATA_DIR, "flags.json")
CONFIG_FILE = os.path.join(CONF_DIR, "config.json")

for file in [SCORE_FILE, SUBMISSION_TRACKER]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

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

def load_config():
    """Load configuration settings from JSON."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
# Configuration
CONFIG = load_config()
TEAM_API_KEYS = {team: details["api_key"] for team, details in CONFIG.get("teams", {}).items()}
NUM_TEAMS = CONFIG.get("num_teams", 5)

# def load_submissions():
#     """Load submitted flags to track duplicate submissions."""
#     return load_json(SUBMISSION_TRACKER)

# def save_submissions(submissions):
#     """Save the updated submission tracker."""
#     save_json(SUBMISSION_TRACKER, submissions)


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

        # Identify the submitting team dynamically
        submitting_team = next((t for t, key in TEAM_API_KEYS.items() if key == api_key), None)
        if not submitting_team:
            return jsonify({"message": "Invalid API key!", "status": "error"}), 403

        # Load flags
        flags = load_json(FLAG_FILE)
        tick = str(flags.get("tick", 0))

        #Load Score
        scores = load_json(SCORE_FILE)
        submitted_flags = load_json(SUBMISSION_TRACKER)

        if not isinstance(submitted_flags, dict):
            submitted_flags = {}

        if tick not in submitted_flags:
            submitted_flags[tick] = []    

        # Check if `flags` is a dictionary
        if not isinstance(flags, dict):
            raise TypeError(f"Invalid flags format: Expected dict, got {type(flags)}")

        # Ensure `flags.json` contains "teams"
        if "teams" not in flags:
            raise KeyError("Missing 'teams' key in flags.json")

        flag_entry = f"{submitting_team}-{submitted_flag}"
        if flag_entry in submitted_flags[tick]:
            return jsonify({"message": "Flag already submitted this tick", "status": "error"}), 400


        teams_flags = flags.get("teams", {})
        # Ensure that the submitting team is not checking its own flag
        for other_team, team_flags in teams_flags.items():
            if not isinstance(team_flags, dict):
                raise TypeError(f"Invalid flag structure for {other_team}: {team_flags}")

            if other_team != submitting_team:
                flag_type = None
                if submitted_flag == team_flags.get("user_flag"):
                    flag_type = "user"
                elif submitted_flag == team_flags.get("root_flag"):
                    flag_type = "root"

                if flag_type:
                    points = 10 if flag_type == "user" else 50
                    scores[submitting_team] = scores.get(submitting_team, 0) + points
                    save_json(SCORE_FILE, scores)

                    submitted_flags[tick].append(flag_entry)
                    save_json(SUBMISSION_TRACKER, submitted_flags)

                    return jsonify({"message": f"{submitting_team} gained {points} points!", "score": scores[submitting_team]})

        return jsonify({"message": "Invalid flag! Submit another team's flag.", "status": "error"}), 400

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
    
@app.route('/scoreboard', methods=['GET'])
def get_scoreboard():
    """Return the scoreboard."""
    scores = load_json(SCORE_FILE)
    return jsonify(scores)

@app.route('/update_config', methods=['POST'])
def update_config():
    """Allows updating the participant configuration from the UI (Admin only)."""
    try:
        auth_key = request.headers.get("Authorization")
        if auth_key != os.getenv("BEARER"):
            return jsonify({"message": "Unauthorized"}), 403

        data = request.json
        if not isinstance(data, dict) or "num_teams" not in data or "teams" not in data:
            return jsonify({"message": "Invalid config format"}), 400

        save_json(CONFIG_FILE, data)

        global CONFIG, TEAM_API_KEYS, NUM_TEAMS
        CONFIG = load_config()
        TEAM_API_KEYS = {team: details["api_key"] for team, details in CONFIG.get("teams", {}).items()}
        NUM_TEAMS = CONFIG.get("num_teams", 5)

        return jsonify({"message": "Configuration updated successfully!"})
    
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500
    
@app.route('/config', methods=['GET'])
def get_config():
    """Returns the current participant configuration."""
    try:
        auth_key = request.headers.get("Authorization")
        if auth_key != os.getenv("BEARER"):
            return jsonify({"message": "Unauthorized"}), 403
        return jsonify(load_config())
    except Exception as e:
        return jsonify({"message": "Internal Server Error"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

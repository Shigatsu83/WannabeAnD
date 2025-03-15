import random
import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FILE = os.path.join(BASE_DIR, "flags.json")

def generate_flag():
    """Generate a random hex-based flag."""
    return f"user{{{random.getrandbits(64):x}}}", f"root{{{random.getrandbits(64):x}}}"

def generate_flags():
    """Generate new flags and save to file."""
    tick = int(time.time() // 180)  # Sync tick every 3 minutes

    flags = {
        "tick": tick,  # Add tick value for synchronization
        "team1": {"user_flag": generate_flag()[0], "root_flag": generate_flag()[1]},
        "team2": {"user_flag": generate_flag()[0], "root_flag": generate_flag()[1]},
        "team3": {"user_flag": generate_flag()[0], "root_flag": generate_flag()[1]}
    }

    with open(FLAG_FILE, "w") as f:
        json.dump(flags, f, indent=4)
    
    print(f"[+] New flags generated at tick {tick} and saved to {FLAG_FILE}")

generate_flags()

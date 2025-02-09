from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the vulnerable machine!"

@app.route('/rce')
def rce():
    cmd = request.args.get("cmd")
    if cmd:
        return os.popen(cmd).read()
    return "Provide ?cmd=yourcommand"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

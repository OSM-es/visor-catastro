
from flask import Flask
app = Flask(__name__)

@app.route("/status")
def status():
    return "ok"

@app.route("/upload")
def upload():
    return "uploading!"

if __name__ == "__main__":
    app.run()
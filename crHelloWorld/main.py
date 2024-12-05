import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Ermmmm, You better work!"

if __name__ == "__main__":
    # Listen on PORT (required for Cloud Run)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

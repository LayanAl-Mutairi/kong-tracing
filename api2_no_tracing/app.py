from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/hello")
def hello():
    return jsonify({"message": "Hello from API2 without manual tracing!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

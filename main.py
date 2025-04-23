from flask import Flask, request, jsonify
import badge_script  # This will be your actual badge code

app = Flask(__name__)

@app.route('/run-badge-script', methods=['POST'])
def run_badge_script():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Assuming badge_script.process_user is a function that processes the username
        badge_script.process_user(username)
        return jsonify({"status": "success", "message": f"Badge graph generated for {username}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "Welcome to BadgeCheck API"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

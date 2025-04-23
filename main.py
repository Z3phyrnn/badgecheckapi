from flask import Flask, request
import badge_script  # This will be your actual badge code

app = Flask(__name__)

@app.route('/run-badge-script', methods=['POST'])
def run_badge_script():
    username = request.json.get("username")
    if not username:
        return {"error": "Username is required"}, 400

    try:
        badge_script.process_user(username)
        return {"status": "success", "message": f"Badge graph generated for {username}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

from flask import Flask, request, jsonify
import badge_script  # Your actual badge code

app = Flask(__name__)

@app.route('/')
def home():
    app.logger.info("Home route accessed")
    return jsonify({"message": "Welcome to BadgeCheck API"}), 200

@app.route('/run-badge-script', methods=['POST'])
def run_badge_script():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        badge_script.process_user(username)
        return jsonify({"status": "success", "message": f"Badge graph generated for {username}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add the new webhook route here
@app.route('/', methods=['POST'])
def webhook():
    data = request.json  # Assuming you're sending JSON data
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Log or process the incoming data
    app.logger.info(f"Webhook data received: {data}")

    # You can add further processing logic for the incoming data here
    # For example, you can call the badge script with data from the webhook

    return jsonify({"status": "success", "message": "Webhook received"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)  # Added debug mode for better logging

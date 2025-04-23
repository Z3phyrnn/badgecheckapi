from flask import Flask, request, jsonify, send_file
import badge_script  # Ensure this has the generate_badge_graph function

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.json
        app.logger.info(f"POST to '/' received. Data: {data}")

        username = data.get("username")
        if not username:
            return jsonify({"error": "Username is required"}), 400

        try:
            badge_path = badge_script.generate_badge_graph(username)
            return send_file(badge_path, mimetype='image/png', as_attachment=True, download_name=f"{username}_badge.png")
        except Exception as e:
            app.logger.error(f"Error generating badge graph for {username}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    # GET method
    app.logger.info("Home route accessed via GET")
    return jsonify({"message": "Welcome to BadgeCheck API"}), 200

@app.route('/run-badge-script', methods=['POST'])
def run_badge_script():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        badge_path = badge_script.generate_badge_graph(username)
        return send_file(badge_path, mimetype='image/png', as_attachment=True, download_name=f"{username}_badge.png")
    except Exception as e:
        app.logger.error(f"Error generating badge graph for {username}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    app.logger.info(f"Webhook data received: {data}")
    
    # Ensure that 'username' is present in the webhook data
    username = data.get("username")
    if not username:
        app.logger.error("Username is required in the webhook data")
        return jsonify({"error": "Username is required in the webhook data"}), 400
    
    try:
        badge_path = badge_script.generate_badge_graph(username)
        return send_file(badge_path, mimetype='image/png', as_attachment=True, download_name=f"{username}_badge.png")
    except Exception as e:
        app.logger.error(f"Webhook error for {username}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)

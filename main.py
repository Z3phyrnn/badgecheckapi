from flask import Flask, request, jsonify, send_file
import badge_script  # Your actual badge code

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # This allows Zapier to POST to the root route without triggering 405 errors
        data = request.json
        app.logger.info(f"POST to '/' received. Data: {data}")
        return jsonify({"status": "success", "message": "POST received at root"}), 200
    # GET method
    app.logger.info("Home route accessed via GET")
    return jsonify({"message": "Welcome to BadgeCheck API"}), 200

@app.route('/run-badge-script', methods=['POST'])
def run_badge_script():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Generate the badge graph
        badge_path = badge_script.generate_badge_graph(username)  # Update to use generate_badge_graph
        
        # Return the generated badge as a file
        return send_file(badge_path, mimetype='image/png', as_attachment=True, download_name=f"{username}_badge.png")

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    app.logger.info(f"Webhook data received: {data}")

    username = data.get("username")
    if username:
        try:
            badge_path = badge_script.generate_badge_graph(username)
            return send_file(badge_path, mimetype='image/png', as_attachment=True, download_name=f"{username}_badge.png")
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"error": "Username is required in the webhook data"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)

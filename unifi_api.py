from flask import Flask, jsonify
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# === Controller Configuration ===
CONTROLLER_URL = "https://192.168.88.50:8443"
USERNAME = "datuan"
PASSWORD = "*Bdu@cds2025"

# === Route: Welcome page ===
@app.route("/", methods=["GET"])
#def index():
#    return """
#    <h2>🎉 UniFi API Server is running!</h2>
#    <p>Try accessing <a href='/api/unifi/devices'>/api/unifi/devices</a> to get device list.</p>
#    """

# === Route: Fetch devices ===
@app.route("/api/unifi/devices", methods=["GET"])
def get_unifi_devices():
    login_url = f"{CONTROLLER_URL}/api/login"
    device_url = f"{CONTROLLER_URL}/api/s/default/stat/device"

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{CONTROLLER_URL}/login",
        "X-Requested-With": "XMLHttpRequest"
    }

    login_payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "remember": True
    }

    # Step 1: Login
    try:
        response = session.post(login_url, json=login_payload, headers=headers, verify=False)
        if response.status_code != 200 or "error" in response.text:
            return jsonify({"error": "Login failed", "details": response.text}), 401
    except Exception as e:
        return jsonify({"error": "Login exception", "details": str(e)}), 500

    # Step 2: Get device list
    try:
        device_response = session.get(device_url, headers=headers, verify=False)
        devices = device_response.json().get("data", [])

        device_list = []
        for d in devices:
            device_info = {
                "name": d.get("name"),
                "ip": d.get("ip"),
                "mac": d.get("mac"),
                "type": d.get("type"),
                "version": d.get("version"),
                "status": "Online" if d.get("state") == 1 else "Offline"
            }
            device_list.append(device_info)

        return jsonify({
            "controller": CONTROLLER_URL,
            "total_devices": len(device_list),
            "devices": device_list
        })

    except Exception as e:
        return jsonify({"error": "Failed to fetch devices", "details": str(e)}), 500

# === Run the Flask server ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)

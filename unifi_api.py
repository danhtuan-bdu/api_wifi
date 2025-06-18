from flask import Flask, jsonify
import requests
import urllib3

# === Disable SSL warnings ===
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# === UniFi Controller Configuration ===
CONTROLLER_URL = "https://192.168.88.50:8443"
USERNAME = "datuan"
PASSWORD = "*Bdu@cds2025"

# === Devices: List of APs and switches ===
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

    try:
        response = session.post(login_url, json=login_payload, headers=headers, verify=False)
        if response.status_code != 200 or "error" in response.text:
            return jsonify({"error": "Login failed", "details": response.text}), 401
    except Exception as e:
        return jsonify({"error": "Login exception", "details": str(e)}), 500

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
                "status": "Online" if d.get("state") == 1 else "Offline",
                "rx_bytes": d.get("rx_bytes", 0),
                "tx_bytes": d.get("tx_bytes", 0),
                "rx_rate_bps": d.get("rx_bytes-r", 0),
                "tx_rate_bps": d.get("tx_bytes-r", 0)
            }
            device_list.append(device_info)

        return jsonify({
            "controller": CONTROLLER_URL,
            "total_devices": len(device_list),
            "devices": device_list
        })

    except Exception as e:
        return jsonify({"error": "Failed to fetch devices", "details": str(e)}), 500


# === Clients: Real-time bandwidth per end user ===
@app.route("/api/unifi/client_bandwidth", methods=["GET"])
def get_client_bandwidth():
    login_url = f"{CONTROLLER_URL}/api/login"
    clients_url = f"{CONTROLLER_URL}/api/s/default/stat/sta"

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

    try:
        response = session.post(login_url, json=login_payload, headers=headers, verify=False)
        if response.status_code != 200 or "error" in response.text:
            return jsonify({"error": "Login failed", "details": response.text}), 401
    except Exception as e:
        return jsonify({"error": "Login exception", "details": str(e)}), 500

    try:
        response = session.get(clients_url, headers=headers, verify=False)
        data = response.json().get("data", [])

        clients = []
        for c in data:
            client_info = {
                "hostname": c.get("hostname"),
                "ip": c.get("ip"),
                "mac": c.get("mac"),
                "essid": c.get("essid"),
                "ap_mac": c.get("ap_mac"),
                "rx_rate_kbps": c.get("rx_rate", 0),  # Download speed
                "tx_rate_kbps": c.get("tx_rate", 0),  # Upload speed
                "rx_bytes": c.get("rx_bytes", 0),
                "tx_bytes": c.get("tx_bytes", 0),
                "signal": c.get("signal"),
                "rssi": c.get("rssi")
            }
            clients.append(client_info)

        return jsonify({
            "controller": CONTROLLER_URL,
            "total_clients": len(clients),
            "clients": clients
        })

    except Exception as e:
        return jsonify({"error": "Client stats failed", "details": str(e)}), 500


# === Run Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)

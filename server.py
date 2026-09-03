"""
server.py — Hapsetme Sorgu Backend v2
──────────────────────────────────────
Kurulum:
    pip install flask flask-cors curl_cffi

Çalıştır:
    python server.py

Deploy: Railway / Render / Replit
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from curl_cffi import requests as cf_requests
import json, os, base64

app = Flask(__name__)
CORS(app, origins="*")

_session = cf_requests.Session(impersonate="chrome124")

ALLOWED_DOMAINS = ["arastir-01.site", "arastir.vip"]

def cf_get(url: str):
    try:
        r = _session.get(url, timeout=20)
        return r.text
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# ── /proxy ──
@app.route("/proxy")
def proxy():
    b64 = request.args.get("b64")
    if b64:
        try:
            url = base64.b64decode(b64).decode("utf-8")
        except Exception:
            return jsonify({"error": "Geçersiz b64"}), 400
    else:
        url = request.args.get("url")

    if not url:
        return jsonify({"error": "url parametresi eksik"}), 400

    if not any(d in url for d in ALLOWED_DOMAINS):
        return jsonify({"error": "İzin verilmeyen domain"}), 403

    result = cf_get(url)
    try:
        return jsonify(json.loads(result))
    except Exception:
        return result, 200, {"Content-Type": "application/json"}

# ── /log/tr ──
@app.route("/log/tr")
def log_tr():
    site = request.args.get("site")
    if not site:
        return jsonify({"error": "site parametresi eksik"}), 400
    try:
        r = _session.get(f"https://wazely.vercel.app/api/trlog?site={site}", timeout=25)
        try:
            return jsonify(json.loads(r.text))
        except Exception:
            return r.text, 200, {"Content-Type": "application/json"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── /log/global ──
@app.route("/log/global")
def log_global():
    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "domain parametresi eksik"}), 400
    try:
        r = _session.get(f"https://wentyn.pythonanywhere.com/extract?domain={domain}", timeout=25)
        return r.text, 200, {
            "Content-Type": "text/plain; charset=utf-8",
            "Access-Control-Allow-Origin": "*"
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── /discord/user/<id> ──
@app.route("/discord/user/<user_id>")
def discord_user(user_id):
    if not user_id.isdigit() or not (5 <= len(user_id) <= 30):
        return jsonify({"error": "Geçersiz kullanıcı ID"}), 400
    try:
        r = _session.get(
            f"https://discord-api-search.bbrraaggee.workers.dev/api/users/{user_id}",
            headers={"Origin": "https://discord-id-hub.info"},
            timeout=10
        )
        try:
            return jsonify(json.loads(r.text))
        except Exception:
            return r.text, r.status_code, {"Content-Type": "application/json"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── /health ──
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Hapsetme Sorgu v2"})

@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "Hapsetme Sorgu Backend v2"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"── Hapsetme Sorgu Backend v2 başlatılıyor... ──")
    print(f"   http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

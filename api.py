from flask import Flask, request, jsonify
import datetime
import json

app = Flask(__name__)

# ========== CONFIG ==========
API_KEY = "satvirflash"
OWNER = "@notxsatvir"
CHANNEL = "https://t.me/freehackingg"
ADMIN_PASSWORD = "admin123"

# ========== STATE ==========
flash_status = "off"
api_banned = False
ban_type = "none"  # none, permanent, temp
ban_until = None
logs = []
users = {}

# ========== HELPERS ==========
def add_log(msg):
    logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(logs) > 100:
        logs.pop(0)

# ========== ROUTES ==========
@app.route('/')
def home():
    return jsonify({
        "api": "Flash API",
        "owner": OWNER,
        "channel": CHANNEL,
        "status": flash_status,
        "banned": api_banned,
        "ban_type": ban_type,
        "ban_until": ban_until,
        "endpoints": {
            "/api?key=satvirflash&action=on": "Turn flash ON",
            "/api?key=satvirflash&action=off": "Turn flash OFF",
            "/api?key=satvirflash&action=status": "Check status",
            "/admin": "Admin panel"
        }
    })

@app.route('/api')
def api():
    key = request.args.get('key')
    action = request.args.get('action', '').lower()
    user_ip = request.remote_addr
    
    # Track user
    if user_ip not in users:
        users[user_ip] = {"count": 0, "last_action": "first_request"}
    users[user_ip]["count"] += 1
    
    if key != API_KEY:
        users[user_ip]["last_action"] = "invalid_key"
        return jsonify({"error": "Invalid API key", "owner": OWNER}), 401
    
    # Check ban
    if api_banned:
        if ban_type == "temp" and ban_until:
            try:
                if datetime.datetime.now() > datetime.datetime.fromisoformat(ban_until):
                    global api_banned, ban_type, ban_until
                    api_banned = False
                    ban_type = "none"
                    ban_until = None
                    add_log("⏰ Temp ban expired, API auto-unbanned")
                else:
                    users[user_ip]["last_action"] = "temp_banned"
                    return jsonify({
                        "error": f"API is temporarily banned until {ban_until}",
                        "owner": OWNER
                    }), 403
            except:
                pass
        else:
            users[user_ip]["last_action"] = "banned"
            return jsonify({"error": "API is permanently banned by admin", "owner": OWNER}), 403
    
    global flash_status
    users[user_ip]["last_action"] = action
    
    if action == 'on':
        flash_status = 'on'
        add_log(f"Flash ON via API (IP: {user_ip})")
        return jsonify({"success": True, "flash": "ON", "owner": OWNER})
    
    elif action == 'off':
        flash_status = 'off'
        add_log(f"Flash OFF via API (IP: {user_ip})")
        return jsonify({"success": True, "flash": "OFF", "owner": OWNER})
    
    elif action == 'status':
        return jsonify({
            "success": True,
            "flash": flash_status,
            "banned": api_banned,
            "ban_type": ban_type,
            "ban_until": ban_until,
            "owner": OWNER,
            "channel": CHANNEL
        })
    
    else:
        return jsonify({
            "error": "Invalid action",
            "actions": ["on", "off", "status"],
            "owner": OWNER
        }), 400

@app.route('/admin')
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Flash Admin</title>
    <style>
        body { background: #0a0a2a; color: white; font-family: Arial; padding: 20px; }
        .card { background: rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; margin-bottom: 16px; border: 1px solid #ff9800; max-width: 500px; margin: auto; }
        h1 { color: #ff9800; text-align: center; }
        .btn { padding: 10px 20px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; margin: 5px; }
        .btn-on { background: #4caf50; color: white; }
        .btn-off { background: #f44336; color: white; }
        .btn-ban { background: #ff9800; color: black; }
        .btn-unban { background: #2196f3; color: white; }
        .btn-temp { background: #ff5722; color: white; }
        .flex { display: flex; flex-wrap: wrap; gap: 5px; }
        .flex .btn { flex: 1; min-width: 80px; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
        .status-on { background: #4caf50; }
        .status-off { background: #f44336; }
        .status-banned { background: #ff9800; color: black; }
        .log-box { background: rgba(0,0,0,0.5); border-radius: 10px; padding: 10px; max-height: 150px; overflow-y: auto; font-size: 11px; }
        .log-entry { padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        a { color: #ff9800; text-decoration: none; }
        .footer { text-align: center; margin-top: 20px; font-size: 11px; color: #666; }
    </style>
    </head>
    <body>
    <div style="max-width:500px; margin:auto;">
    <h1>⚡ Flash API Admin</h1>
    <p style="text-align:center; color:#ff6666;">Owner: @notxsatvir</p>
    
    <div class="card">
        <h3>📊 Status</h3>
        <p>Flash: <span class="status-badge status-''' + flash_status + '''">''' + flash_status.upper() + '''</span></p>
        <p>API: <span class="status-badge ''' + ('status-banned' if api_banned else 'status-on') + '''">''' + ('BANNED' if api_banned else 'ACTIVE') + '''</span></p>
        <p style="font-size:12px; color:#888;">Ban Type: ''' + ban_type + '''</p>
        <p style="font-size:12px; color:#888;">Users: ''' + str(len(users)) + '''</p>
    </div>
    
    <div class="card">
        <h3>🎮 Controls</h3>
        <div class="flex">
            <a href="/admin/on" class="btn btn-on">💡 ON</a>
            <a href="/admin/off" class="btn btn-off">💡 OFF</a>
        </div>
    </div>
    
    <div class="card">
        <h3>🚫 Ban Controls</h3>
        <div class="flex">
            <a href="/admin/ban" class="btn btn-ban">🚫 Permanent</a>
            <a href="/admin/tempban/5" class="btn btn-temp">⏱️ 5 min</a>
            <a href="/admin/tempban/10" class="btn btn-temp">⏱️ 10 min</a>
            <a href="/admin/tempban/60" class="btn btn-temp">⏱️ 1 hour</a>
            <a href="/admin/unban" class="btn btn-unban">✅ Unban</a>
        </div>
    </div>
    
    <div class="card">
        <h3>📜 Logs</h3>
        <div class="log-box">
            ''' + ''.join([f'<div class="log-entry">{log}</div>' for log in logs[-15:]]) + '''
        </div>
        <p style="margin-top:8px;"><a href="/admin/clearlogs" class="btn btn-ban" style="display:inline-block;padding:8px 16px;border-radius:10px;background:#ff9800;color:black;text-decoration:none;">🗑️ Clear Logs</a></p>
    </div>
    
    <div class="card">
        <h3>🔑 API Info</h3>
        <p><strong>Key:</strong> satvirflash</p>
        <p style="font-size:11px; word-break:break-all; background:#000; padding:8px; border-radius:8px;">
        /api?key=satvirflash&action=on<br>
        /api?key=satvirflash&action=off<br>
        /api?key=satvirflash&action=status
        </p>
    </div>
    
    <div class="footer">⚡ SATVIR FLASH API | @notxsatvir</div>
    </div>
    </body>
    </html>
    '''

@app.route('/admin/on')
def admin_on():
    global flash_status
    flash_status = 'on'
    add_log("Flash ON by admin")
    return '<script>alert("✅ Flash turned ON!"); window.location="/admin";</script>'

@app.route('/admin/off')
def admin_off():
    global flash_status
    flash_status = 'off'
    add_log("Flash OFF by admin")
    return '<script>alert("✅ Flash turned OFF!"); window.location="/admin";</script>'

@app.route('/admin/ban')
def admin_ban():
    global api_banned, ban_type, ban_until
    api_banned = True
    ban_type = "permanent"
    ban_until = None
    add_log("🚫 API permanently banned by admin")
    return '<script>alert("🚫 API permanently banned!"); window.location="/admin";</script>'

@app.route('/admin/unban')
def admin_unban():
    global api_banned, ban_type, ban_until
    api_banned = False
    ban_type = "none"
    ban_until = None
    add_log("✅ API unbanned by admin")
    return '<script>alert("✅ API unbanned!"); window.location="/admin";</script>'

@app.route('/admin/tempban/<int:minutes>')
def admin_tempban(minutes):
    global api_banned, ban_type, ban_until
    api_banned = True
    ban_type = "temp"
    ban_until = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).isoformat()
    add_log(f"⏱️ API temp banned for {minutes} minutes")
    return f'<script>alert("⏱️ API temp banned for {minutes} minutes!"); window.location="/admin";</script>'

@app.route('/admin/clearlogs')
def admin_clearlogs():
    global logs
    logs = []
    add_log("🗑️ Logs cleared by admin")
    return '<script>alert("🗑️ Logs cleared!"); window.location="/admin";</script>'

@app.route('/health')
def health():
    return jsonify({"status": "ok", "owner": OWNER})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

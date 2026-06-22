from flask import Flask, request, jsonify, render_template_string
import datetime
import os

app = Flask(__name__)

# ========== CONFIG ==========
API_KEY = "satvirflash"
OWNER = "@notxsatvir"
CHANNEL = "https://t.me/freehackingg"
ADMIN_PASSWORD = "admin123"

# ========== STATE ==========
flash_status = "off"
api_banned = False
logs = []

# ========== ADMIN HTML ==========
ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Flash API Admin</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a2a, #1a0000);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        .container { max-width: 550px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { color: #ff9800; font-size: 28px; }
        .header p { color: #ff6666; }
        .card {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,152,0,0.2);
        }
        .card h3 { color: #ff9800; margin-bottom: 12px; font-size: 15px; }
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 14px;
        }
        .status-on { background: #4caf50; color: white; }
        .status-off { background: #f44336; color: white; }
        .status-banned { background: #ff9800; color: black; }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: transform 0.15s;
            margin: 4px;
        }
        .btn:active { transform: scale(0.95); }
        .btn-on { background: #4caf50; color: white; }
        .btn-off { background: #f44336; color: white; }
        .btn-ban { background: #ff9800; color: black; }
        .btn-unban { background: #2196f3; color: white; }
        .btn-logout { background: #dc3545; color: white; }
        .flex { display: flex; gap: 8px; flex-wrap: wrap; }
        .flex .btn { flex: 1; min-width: 100px; }
        .log-box {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 12px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 11px;
        }
        .log-entry { padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color: #aaa; }
        .log-entry .time { color: #ff9800; }
        input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 10px;
            background: rgba(0,0,0,0.5);
            color: white;
            border: 1px solid #ff9800;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .api-box {
            background: rgba(0,0,0,0.4);
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            color: #ff9800;
            margin: 8px 0;
        }
        .footer { text-align: center; font-size: 10px; color: #666; margin-top: 20px; }
        @media (max-width: 400px) { .flex { flex-direction: column; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ FLASH API ADMIN</h1>
            <p>Owner: {{ owner }}</p>
        </div>

        {% if not logged_in %}
        <div class="card" style="text-align:center; padding:30px;">
            <h3>🔐 Admin Login</h3>
            <form method="POST">
                <input type="password" name="password" placeholder="Enter admin password" required>
                <button type="submit" class="btn btn-on" style="width:100%;">Login</button>
            </form>
        </div>
        {% else %}

        <div class="card">
            <h3>📊 Status</h3>
            <p>Flash: <span class="status-badge status-{{ flash_status }}">{{ flash_status.upper() }}</span></p>
            <p>API: <span class="status-badge {% if api_banned %}status-banned{% else %}status-on{% endif %}">
                {% if api_banned %}BANNED{% else %}ACTIVE{% endif %}
            </span></p>
        </div>

        <div class="card">
            <h3>🎮 Controls</h3>
            <div class="flex">
                <form method="POST" style="flex:1;">
                    <input type="hidden" name="action" value="on">
                    <button type="submit" class="btn btn-on" style="width:100%;">💡 ON</button>
                </form>
                <form method="POST" style="flex:1;">
                    <input type="hidden" name="action" value="off">
                    <button type="submit" class="btn btn-off" style="width:100%;">💡 OFF</button>
                </form>
            </div>
            <div class="flex" style="margin-top:8px;">
                <form method="POST" style="flex:1;">
                    <input type="hidden" name="action" value="ban">
                    <button type="submit" class="btn btn-ban" style="width:100%;">🚫 Ban</button>
                </form>
                <form method="POST" style="flex:1;">
                    <input type="hidden" name="action" value="unban">
                    <button type="submit" class="btn btn-unban" style="width:100%;">✅ Unban</button>
                </form>
            </div>
        </div>

        <div class="card">
            <h3>🔑 API Info</h3>
            <p><strong>Key:</strong> <code>{{ api_key }}</code></p>
            <div class="api-box">
                /api?key=satvirflash&action=on<br>
                /api?key=satvirflash&action=off<br>
                /api?key=satvirflash&action=status
            </div>
        </div>

        <div class="card">
            <h3>📜 Logs</h3>
            <div class="log-box">
                {% for log in logs %}
                <div class="log-entry">{{ log }}</div>
                {% endfor %}
            </div>
            <form method="POST" style="margin-top:8px;">
                <input type="hidden" name="action" value="clearlogs">
                <button type="submit" class="btn btn-ban" style="width:100%;">🗑️ Clear Logs</button>
            </form>
        </div>

        <form method="POST">
            <input type="hidden" name="action" value="logout">
            <button type="submit" class="btn btn-logout" style="width:100%;">🚪 Logout</button>
        </form>

        {% endif %}

        <div class="footer">⚡ SATVIR FLASH API | @notxsatvir</div>
    </div>
</body>
</html>
'''

# ========== ROUTES ==========
@app.route('/')
def home():
    return jsonify({
        "api": "Flash API",
        "owner": OWNER,
        "channel": CHANNEL,
        "status": flash_status,
        "banned": api_banned,
        "endpoints": {
            "/api?key=satvirflash&action=on": "Turn flash ON",
            "/api?key=satvirflash&action=off": "Turn flash OFF",
            "/api?key=satvirflash&action=status": "Check status",
            "/admin": "Admin panel"
        },
        "note": "Use in mobile browser for flashlight control"
    })

@app.route('/api')
def api():
    key = request.args.get('key')
    action = request.args.get('action', '').lower()
    
    if key != API_KEY:
        return jsonify({"error": "Invalid API key", "owner": OWNER}), 401
    
    if api_banned:
        return jsonify({"error": "API is banned by admin", "owner": OWNER}), 403
    
    global flash_status
    if action == 'on':
        flash_status = 'on'
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Flash ON via API")
        return jsonify({"success": True, "flash": "ON", "owner": OWNER})
    
    elif action == 'off':
        flash_status = 'off'
        logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Flash OFF via API")
        return jsonify({"success": True, "flash": "OFF", "owner": OWNER})
    
    elif action == 'status':
        return jsonify({
            "success": True,
            "flash": flash_status,
            "banned": api_banned,
            "owner": OWNER,
            "channel": CHANNEL
        })
    
    else:
        return jsonify({
            "error": "Invalid action",
            "actions": ["on", "off", "status"],
            "owner": OWNER
        }), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    logged_in = request.cookies.get('admin_session') == 'true'
    
    if request.method == 'POST':
        password = request.form.get('password')
        action = request.form.get('action')
        
        if password == ADMIN_PASSWORD:
            logged_in = True
            response = app.make_response(render_template_string(ADMIN_HTML, 
                logged_in=True,
                flash_status=flash_status,
                api_banned=api_banned,
                logs=logs[-30:],
                api_key=API_KEY,
                owner=OWNER
            ))
            response.set_cookie('admin_session', 'true', max_age=3600)
            return response
        
        elif action == 'logout':
            logged_in = False
            response = app.make_response(render_template_string(ADMIN_HTML, logged_in=False))
            response.set_cookie('admin_session', '', expires=0)
            return response
        
        elif logged_in:
            global flash_status, api_banned
            if action == 'on':
                flash_status = 'on'
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Flash ON by admin")
            elif action == 'off':
                flash_status = 'off'
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Flash OFF by admin")
            elif action == 'ban':
                api_banned = True
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] API BANNED by admin")
            elif action == 'unban':
                api_banned = False
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] API UNBANNED by admin")
            elif action == 'clearlogs':
                logs.clear()
                logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Logs cleared by admin")
    
    if logged_in:
        return render_template_string(ADMIN_HTML,
            logged_in=True,
            flash_status=flash_status,
            api_banned=api_banned,
            logs=logs[-30:],
            api_key=API_KEY,
            owner=OWNER
        )
    
    return render_template_string(ADMIN_HTML, logged_in=False)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "owner": OWNER})

# ========== VERCEL REQUIRED ==========
# Vercel needs this variable named 'app'
# app is already defined above

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

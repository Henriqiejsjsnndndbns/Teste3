from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from pynput.mouse import Controller, Button
import socket
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mouse = Controller()

PASSWORD = str(random.randint(1000, 9999))
clients = set()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

@app.route("/")
def home():
    ip = get_ip()

    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin:0;
                background:#000;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                overflow:hidden;
            }}

            #btn {{
                width:200px;
                height:200px;
                border-radius:50%;
                background:#00ff88;
                border:none;
                font-size:18px;
                font-weight:bold;
            }}

            #btn:active {{
                transform:scale(0.95);
                background:#00cc66;
            }}

            #info {{
                position:absolute;
                top:10px;
                color:#0f0;
                font-family:monospace;
                font-size:12px;
            }}
        </style>
    </head>

    <body>
        <div id="info">
            IP: {ip}:5000 | SENHA: {PASSWORD}
        </div>

        <button id="btn">TOQUE</button>

        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <script>
            const socket = io();
            let lastTap = 0;

            socket.emit("auth", {{password: "{PASSWORD}"}});

            document.getElementById("btn").addEventListener("click", () => {{
                const now = new Date().getTime();
                const diff = now - lastTap;

                if(diff < 300) {{
                    socket.emit("click"); // duplo clique
                }} else {{
                    socket.emit("move", {{x: 15, y: 0}}); // move leve
                }}

                lastTap = now;
            }});
        </script>
    </body>
    </html>
    """)

@socketio.on("auth")
def auth(data):
    if data.get("password") == PASSWORD:
        clients.add(request.sid)
        emit("ok")

@socketio.on("move")
def move(data):
    if request.sid in clients:
        mouse.move(float(data["x"]), float(data["y"]))

@socketio.on("click")
def click():
    if request.sid in clients:
        mouse.click(Button.left, 1)

if __name__ == "__main__":
    print("Servidor rodando...")
    print("Senha:", PASSWORD)
    socketio.run(app, host="0.0.0.0", port=5000)

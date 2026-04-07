import socket
import webview
import threading
import app as bunny

def get_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

port = get_port()

def run_flask():
    bunny.app.run(port=port)

t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

webview.create_window(f"{bunny.__APP__} v{bunny.__VERSION__}", f"http://127.0.0.1:{port}")
webview.start()
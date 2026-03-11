import webview
import threading
import os
import http.server
import socketserver
import sys
import time

# --- Configuration ---
DIRECTORY = "content"
INDEX_FILE = "index.html"
# Global to store the port assigned by the OS
actual_port = 0


def start_server():
    """Background task to serve the 'content' folder."""
    global actual_port

    # Change to the directory we want to serve
    os.chdir(os.path.join(os.getcwd(), DIRECTORY))

    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True

    # Port 0 tells the OS to find any free port
    with socketserver.TCPServer(("", 0), handler) as httpd:
        actual_port = httpd.socket.getsockname()[1]
        print(f"Internal server started on port {actual_port}")
        httpd.serve_forever()


def show_missing_data_error():
    """Opens a UI window explaining that scraper.py needs to be run."""
    error_html = """
    <body style="background: #121212; color: #e8eaed; font-family: sans-serif; 
                 display: flex; flex-direction: column; align-items: center; 
                 justify-content: center; height: 100vh; text-align: center; margin: 0;">
        <h1 style="color: #ff8a80; font-size: 2rem;">⚠️ Content Missing</h1>
        <p style="font-size: 1.1rem; max-width: 80%;">The offline database has not been built yet.</p>
        <div style="background: #1e1e1e; padding: 20px; border-radius: 8px; 
                    border: 1px solid #3c4043; margin: 20px; font-family: monospace;">
            python scraper.py
        </div>
        <p style="color: #9aa0a6;">Please run the scraper first to generate the tutorial files.</p>
    </body>
    """
    window = webview.create_window(
        "Setup Required", html=error_html, width=500, height=450, resizable=False
    )
    webview.start()


if __name__ == "__main__":
    # 1. Check if the content exists before starting
    target_path = os.path.join(os.getcwd(), DIRECTORY, INDEX_FILE)

    if not os.path.exists(target_path):
        print("Error: index.html not found! Showing GUI error.")
        show_missing_data_error()
        sys.exit()

    # 2. Start the server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 3. Wait for the server to report its port
    while actual_port == 0:
        time.sleep(0.1)

    # 4. Launch the Main UI
    try:
        webview.create_window(
            "LearnCPP Offline Reader",
            f"http://localhost:{actual_port}/{INDEX_FILE}",
            width=1200,
            height=850,
            confirm_close=True,
        )
        webview.start()
    except Exception as e:
        print(f"Failed to launch WebView: {e}")

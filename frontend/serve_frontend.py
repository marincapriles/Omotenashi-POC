import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "static"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)  # Change to the static directory
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving static files at http://localhost:{PORT}")
        httpd.serve_forever() 
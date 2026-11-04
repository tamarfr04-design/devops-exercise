import html
import os
import signal
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MESSAGE = "Hello again - deployed with zero downtime!"
VERSION = os.getenv("APP_VERSION", "dev")
POD_NAME = os.getenv("POD_NAME", socket.gethostname())
PORT = int(os.getenv("PORT", "8080"))

PAGE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>DevOps Exercise</title></head>
<body style="font-family: sans-serif; margin: 3rem;">
  <h1>{message}</h1>
  <p><strong>Version:</strong> {version}</p>
  <p><strong>Pod:</strong> {pod}</p>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, "text/plain", b"ok\n")
        elif self.path == "/":
            body = PAGE.format(
                message=html.escape(MESSAGE),
                version=html.escape(VERSION),
                pod=html.escape(POD_NAME),
            ).encode()
            self._send(200, "text/html; charset=utf-8", body)
        else:
            self._send(404, "text/plain", b"not found\n")

    def _send(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

    # On SIGTERM (sent by Kubernetes when stopping a pod), stop accepting new
    # requests and exit cleanly instead of being killed mid-request.
    def shutdown(signum, frame):
        threading.Thread(target=server.shutdown).start()

    signal.signal(signal.SIGTERM, shutdown)
    print(f"Listening on :{PORT}, version={VERSION}, pod={POD_NAME}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
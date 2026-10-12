"""A minimal HTTP endpoint for the provider's webhooks."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from .webhooks import SignatureError


def make_handler(webhook_handler):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            signature = self.headers.get("X-Signature")
            try:
                event = webhook_handler.handle(body, signature)
            except SignatureError:
                self._reply(401, {"error": "bad signature"})
                return
            except (KeyError, ValueError):
                self._reply(400, {"error": "malformed event"})
                return
            self._reply(202, {"accepted": event.event_id})

        def _reply(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):  # keep the test output quiet
            return

    return Handler


def serve(webhook_handler, host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), make_handler(webhook_handler))
    server.serve_forever()

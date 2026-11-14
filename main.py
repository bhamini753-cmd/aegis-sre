import os
import json
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from config import Config
from mock_infra import infra
from agent import sre_agent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "static", "index.html")


class AegisSRERequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status_code: int = 200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html"):
            if os.path.exists(INDEX_PATH):
                with open(INDEX_PATH, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_json({"error": f"Missing file: {INDEX_PATH}"}, 404)

        elif self.path == "/api/state":
            self._send_json(infra.get_cluster_state())

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        if self.path == "/api/inject":
            body = json.loads(raw_body or "{}")
            scenario_id = body.get("scenario_id", "memory_leak")
            self._send_json(infra.inject_incident(scenario_id))

        elif self.path == "/api/run-agent":
            self._send_json(sre_agent.run_incident_response())

        elif self.path == "/api/reset":
            self._send_json(infra.reset_cluster())

        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[AegisSRE Server] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    server_address = (Config.HOST, Config.PORT)
    httpd = ThreadingHTTPServer(server_address, AegisSRERequestHandler)
    url = f"http://localhost:{Config.PORT}"
    print(f"\n=======================================================")
    print(f" AegisSRE Agent is LIVE at: {url}")
    print(f" (Keep this window open and use your browser)")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    httpd.serve_forever()
"""
A tiny local REST API used as the project's "external API" source.

The assignment allows using a public API OR building a local Mock API
when internet access is not guaranteed. To keep the project runnable
anywhere with zero external dependencies, this module spins up a real
HTTP server (stdlib only, no Flask) on 127.0.0.1 that serves student
academic data as JSON. app/sources/api_source.py then talks to it with
plain `requests` calls, exactly like it would talk to any real REST API.

The response data intentionally includes a few bad records (an invalid
GPA, an invalid attendance percentage, a missing GPA, and a student_id
that does not exist in the CSV) so the validation stage has something
real to catch.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Academic data keyed by student_id. Deliberately includes bad values.
ACADEMIC_RECORDS = [
    {"student_id": 1001, "gpa": 3.8, "attendance": 95, "status": "Active"},
    {"student_id": 1002, "gpa": 3.2, "attendance": 88, "status": "Active"},
    {"student_id": 1003, "gpa": 2.9, "attendance": 76, "status": "Active"},
    {"student_id": 1004, "gpa": 3.5, "attendance": 91, "status": "Active"},
    {"student_id": 1005, "gpa": 2.1, "attendance": 60, "status": "Probation"},
    {"student_id": 1006, "gpa": None, "attendance": 82, "status": "Active"},
    {"student_id": 1007, "gpa": 4.9, "attendance": 70, "status": "Active"},
    {"student_id": 1008, "gpa": 3.0, "attendance": 55, "status": "Active"},
    {"student_id": 1009, "gpa": 2.7, "attendance": 105, "status": "Active"},
    {"student_id": 1010, "gpa": 3.9, "attendance": 93, "status": "Active"},
    {"student_id": 1011, "gpa": 3.1, "attendance": 40, "status": "Probation"},
    {"student_id": 1012, "gpa": 2.4, "attendance": 85, "status": "Active"},
    {"student_id": 1013, "gpa": 1.8, "attendance": 30, "status": "Probation"},
    {"student_id": 1014, "gpa": 3.6, "attendance": 89, "status": "Active"},
    {"student_id": 1015, "gpa": 2.0, "attendance": 77, "status": "Active"},
    {"student_id": 1016, "gpa": 3.95, "attendance": 97, "status": "Active"},
    {"student_id": 1017, "gpa": 2.2, "attendance": 68, "status": "Active"},
    # Orphan record: exists in the API but not in the CSV source.
    {"student_id": 1099, "gpa": 3.0, "attendance": 80, "status": "Active"},
]


class _StudentsAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - silence default access log
        pass

    def do_GET(self):  # noqa: N802 - required name by BaseHTTPRequestHandler
        if self.path.rstrip("/") == "/students":
            self._send_json(200, ACADEMIC_RECORDS)
            return

        if self.path.startswith("/students/"):
            try:
                student_id = int(self.path.split("/students/")[1])
            except ValueError:
                self._send_json(400, {"error": "invalid student_id"})
                return
            record = next(
                (r for r in ACADEMIC_RECORDS if r["student_id"] == student_id), None
            )
            if record is None:
                self._send_json(404, {"error": "not found"})
            else:
                self._send_json(200, record)
            return

        self._send_json(404, {"error": "unknown endpoint"})

    def _send_json(self, status_code: int, payload) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


_server_lock = threading.Lock()
_server_thread: threading.Thread | None = None
_httpd: ThreadingHTTPServer | None = None


def start_mock_api_server(host: str = "127.0.0.1", port: int = 8899) -> None:
    """Idempotently start the mock API server in a background thread."""
    global _server_thread, _httpd
    with _server_lock:
        if _server_thread is not None and _server_thread.is_alive():
            return
        _httpd = ThreadingHTTPServer((host, port), _StudentsAPIHandler)
        _server_thread = threading.Thread(target=_httpd.serve_forever, daemon=True)
        _server_thread.start()


def stop_mock_api_server() -> None:
    global _server_thread, _httpd
    with _server_lock:
        if _httpd is not None:
            _httpd.shutdown()
            _httpd.server_close()
        _httpd = None
        _server_thread = None

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from app.services.timeline_service import TimelineService
from app.storage.json_timeline_repository import JsonTimelineRepository


class TimelineRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, service: TimelineService, **kwargs: object) -> None:
        self.service = service
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if urlsplit(self.path).path.startswith("/api/"):
            self._handle_api_get()
        else:
            super().do_GET()

    def do_POST(self) -> None:
        self._handle_api_write("POST")

    def do_PUT(self) -> None:
        self._handle_api_write("PUT")

    def do_DELETE(self) -> None:
        self._handle_api_write("DELETE")

    def _handle_api_get(self) -> None:
        parsed_url = urlsplit(self.path)
        if parsed_url.path != "/api/events":
            self._send_error(404, "API endpoint not found.")
            return

        query = parse_qs(parsed_url.query)
        direction = query.get("direction", ["forward"])[0]
        if direction not in ("forward", "reverse"):
            self._send_error(400, "Direction must be 'forward' or 'reverse'.")
            return

        events = self.service.list_events(reverse=direction == "reverse")
        self._send_json(
            200,
            {"events": [event.to_dict() for event in events], "count": len(events)},
        )

    def _handle_api_write(self, method: str) -> None:
        parsed_url = urlsplit(self.path)
        if parsed_url.path == "/api/events" and method == "POST":
            try:
                payload = self._read_json_body()
                if not isinstance(payload, dict):
                    raise ValueError("Request body must be a JSON object.")
                insertion_index = payload.get("index")
                event = self.service.create_event(payload, insertion_index)
            except (ValueError, json.JSONDecodeError) as error:
                self._send_error(400, str(error))
                return
            self._send_json(201, {"event": event.to_dict()})
            return

        prefix = "/api/events/"
        if not parsed_url.path.startswith(prefix):
            self._send_error(404, "API endpoint not found.")
            return

        event_id = unquote(parsed_url.path[len(prefix):])
        if not event_id or "/" in event_id:
            self._send_error(404, "Timeline entry not found.")
            return

        if method == "DELETE":
            try:
                event = self.service.delete_event(event_id)
            except KeyError as error:
                self._send_error(404, str(error))
                return
            self._send_json(200, {"event": event.to_dict()})
            return

        if method == "PUT":
            try:
                payload = self._read_json_body()
                if not isinstance(payload, dict):
                    raise ValueError("Request body must be a JSON object.")
                event = self.service.update_event(event_id, payload)
            except (ValueError, json.JSONDecodeError) as error:
                self._send_error(400, str(error))
                return
            except KeyError as error:
                self._send_error(404, str(error))
                return
            self._send_json(200, {"event": event.to_dict()})
            return

        self._send_error(405, "Method not allowed.")

    def _read_json_body(self) -> object:
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            raise ValueError("Content-Length header is required.")
        try:
            length = int(content_length)
        except ValueError as error:
            raise ValueError("Content-Length must be an integer.") from error
        if length < 0 or length > 1_000_000:
            raise ValueError("Request body must be 1 MB or smaller.")
        return json.loads(self.rfile.read(length))

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(static_directory: Path, data_file: Path, port: int = 8000) -> None:
    service = TimelineService(JsonTimelineRepository(data_file))
    handler = partial(
        TimelineRequestHandler,
        service=service,
        directory=str(static_directory),
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Pelagos timeline is running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()

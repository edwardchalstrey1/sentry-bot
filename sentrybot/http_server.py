import io
import logging
import socketserver
from http import server
from threading import Condition
from typing import Final
from urllib.parse import parse_qs

import picamera  # type: ignore # pylint: disable=import-error

from sentrybot.turret_controller import TurretController

turret_controller: Final[TurretController] = TurretController()


with open("templates/simpleserver.html", "r") as the_file:
    PAGE: Final[str] = the_file.read()


class StreamingOutput:
    def __init__(self) -> None:
        self.frame = bytes()
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf: bytes) -> int:
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
                raise
        elif self.path.startswith("/ajax-data"):
            parsed = parse_qs(self.path[len("/ajax-data?") :])
            logging.warning("received ajax data: {}".format(parsed))
            # turret_controller.launch()

            # Still getting ERR_EMPTY_RESPONSE
            self.send_response(200)
        else:
            # self.send_error(404)
            # self.end_headers()
            super().do_GET()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with picamera.PiCamera(resolution="640x480", framerate=24) as camera:

    output = StreamingOutput()
    camera.rotation = 270
    camera.start_recording(output, format="mjpeg")
    try:
        address = ("", 8000)
        my_server = StreamingServer(address, StreamingHandler)
        logging.warning("serving")
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.warning("exiting")
        camera.stop_recording()
        turret_controller.reset()

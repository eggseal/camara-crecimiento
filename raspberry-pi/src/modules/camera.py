import logging
import threading
import time

import cv2
import websocket
import config

CAM_WIDTH = 320
CAM_HEIGHT = 240
CAM_FPS = 10
JPEG_QUALITY = 70

encoding = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]


class CameraThread(threading.Thread):
    cameras = []

    def __init__(self, id: int, device: str, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.id = id
        self.device = device
        self.stop_event = stop_event

        self.capture = cv2.VideoCapture(self.device)
        if not self.capture.isOpened():
            raise RuntimeError(f"Camera {device} failed to open")

        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # type: ignore
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.capture.set(cv2.CAP_PROP_FPS, CAM_FPS)

        self.ws = None
        self.last_connect_attempt = 0
        self.lock = threading.Lock()
        self.frame = None
        CameraThread.cameras.append(self)

    def connect_ws(self):
        url = f"wss://{config.STREAM_SERVER_URL}/ws/cam/{self.id}"
        logging.info("Connecting to Web Socket %s", url)
        try:
            ws = websocket.create_connection(url, timeout=5)
            logging.info("WebSocket connected for camera %d", self.id)
            return ws
        except Exception as e:
            logging.error("WebSocket connection failed for camera %d: %s", self.id, e)
            return None

    def run(self):
        issued_warning = False
        while not self.stop_event.is_set():
            status, frame = self.capture.read()
            # Failed to read camera
            if not status or frame is None or frame.size == 0:
                if not issued_warning:
                    logging.warning("Camera %d failed during reading", self.id)
                    issued_warning = True
                time.sleep(1.0 / CAM_FPS)
                continue
            # Store current frame
            with self.lock:
                self.frame = frame.copy()
            success, jpeg = cv2.imencode(".jpg", frame, encoding)
            if not success:
                continue
            # Reconnect to WS every 5 seconds if disconnected
            if self.ws is None:
                if time.time() - self.last_connect_attempt > 5:
                    logging.info("Attempting to reconnect to web socket.")
                    self.last_connect_attempt = time.time()
                    self.ws = self.connect_ws()
            # Send current frame to web socket
            if self.ws:
                try:
                    self.ws.send(jpeg.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
                except Exception:
                    logging.warning("WebSocket disconnected for camera %d", self.id)
                    try:
                        self.ws.close()
                    except Exception:
                        pass
                    self.ws = None
            time.sleep(1.0 / CAM_FPS)

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def release(self):
        self.capture.release()

        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

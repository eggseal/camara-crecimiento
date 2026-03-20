import logging
import subprocess
import threading
import time

import cv2

import config
import utils

CAM_WIDTH = 320
CAM_HEIGHT = 240
CAM_FPS = 10
RTMP_CMD = [
    "ffmpeg",
    "-f",
    "rawvideo",
    "-pix_fmt",
    "bgr24",
    "-s",
    f"{CAM_WIDTH}x{CAM_HEIGHT}",
    "-r",
    str(CAM_FPS),
    "-i",
    "-",
    "-vcodec",
    "libx264",
    "-preset",
    "ultrafast",
    "-tune",
    "zerolatency",
    "-g",
    "10",
    "-keyint_min",
    "10",
    "-b:v",
    "1000k",
    "-f",
    "flv",
    "rtmp://{url}:{port}/live/modulo-{idx}",
]


class CameraThread(threading.Thread):
    cameras = []

    def __init__(self, id: int, device: str, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.id = id
        self.device = device
        self.stop_event = stop_event


        self.capture = cv2.VideoCapture(self.device)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))  # type: ignore
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.capture.set(cv2.CAP_PROP_FPS, CAM_FPS)

        self.cmd = RTMP_CMD.copy()
        self.cmd[-1] = self.cmd[-1].format(
            url=config.STREAM_SERVER_URL, port=config.STREAM_SERVER_PORT, idx=self.id
        )
        self.rtmp_client = self.start_ffmpeg()
        self.last_restart_attempt = 0

        self.lock = threading.Lock()
        self.frame = None

        CameraThread.cameras.append(self)

    def start_ffmpeg(self):
        return subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run(self):
        issued_warning = False

        while not self.stop_event.is_set():
            status, frame = self.capture.read()
            if not status or frame is None or frame.size == 0:
                if not issued_warning:
                    logging.warning("Camera %d failed during reading", self.id)
                    issued_warning = True
                time.sleep(1.0 / CAM_FPS)
                continue

            with self.lock:
                self.frame = frame.copy()

            ffmpeg_alive = self.rtmp_client and self.rtmp_client.poll() is None
            if ffmpeg_alive:
                try:
                    if self.rtmp_client and self.rtmp_client.stdin:
                        self.rtmp_client.stdin.write(frame.tobytes())
                except BrokenPipeError:
                    logging.error("FFmpeg pipe broken for camera %d", self.id)
                    self.rtmp_client = None
            else:
                if time.time() - self.last_restart_attempt > 5:
                    self.last_restart_attempt = time.time()

                    if utils.has_internet():
                        logging.info("Restarting FFmpeg for camera %d", self.id)
                        try:
                            self.rtmp_client = self.start_ffmpeg()
                        except Exception as e:
                            logging.error("Failed to restart FFmpeg: %s", e)
                    else:
                        logging.warning("No internet, skipping FFmpeg restart")
            time.sleep(1.0 / CAM_FPS)

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def release(self):
        self.capture.release()

        if self.rtmp_client:
            try:
                if self.rtmp_client.stdin:
                    self.rtmp_client.stdin.close()
            except Exception:
                pass

            self.rtmp_client.terminate()
            self.rtmp_client.wait()

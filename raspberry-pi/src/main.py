import threading

import config
from modules.camera import CameraThread

stop_event = threading.Event()
CameraThread(1, config.STREAM_DEVICE1, stop_event)
CameraThread(2, config.STREAM_DEVICE2, stop_event)

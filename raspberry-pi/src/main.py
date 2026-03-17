import logging
import threading
import time
import json
from datetime import datetime

import config
import serial
from modules.camera import CameraThread

stop_event = threading.Event()
CameraThread(1, config.STREAM_DEVICE1, stop_event)
CameraThread(2, config.STREAM_DEVICE2, stop_event)
modules = (
    serial.Serial(config.MODULE_DEVICE1, 115200, timeout=5), 
    serial.Serial(config.MODULE_DEVICE2, 115200, timeout=5)
)


def main():
    timestamp = datetime.now()
    for module in modules:
        module.reset_input_buffer()
        module.write(json.dumps({"cmd": 1}).encode() + b"\n")
        module.flush()
        
        res = json.loads(module.readline().decode().strip())
        if res == b"":
            logging.error("Timed out waiting for ESP32 response.")
            continue
        res["timestamp"] = timestamp
        logging.info(res)


if __name__ == "__main__":
    try:
        while True:
            main()
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Exiting the program...")
    finally:
        stop_event.set()

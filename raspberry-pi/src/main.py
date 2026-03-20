import logging
import threading
import time
import json
from json import JSONDecodeError
from datetime import datetime

import config   
import serial
import serial.tools.list_ports as list_ports
from modules.camera import CameraThread

stop_event = threading.Event()
CameraThread(1, config.STREAM_DEVICE1, stop_event)
CameraThread(2, config.STREAM_DEVICE2, stop_event)
module_lock = threading.Lock()
modules: list[serial.Serial] = []

COMMANDS = {
    "READ_ALL": lambda: json.dumps({"cmd": 1}).encode() + b"\n"
}


def reconnect_modules():
    while not stop_event.is_set():
        ports = list_ports.comports(include_links=True)
        for port in ports:
            if port.vid is None: continue
            with module_lock:
                if any(mod.port == port.device for mod in modules): continue

            try:
                logging.info("Attempting serial connection with device %s", port.device)
                ser = serial.Serial(port.device, 115200, timeout=1)
                with module_lock:
                    modules.append(ser)
                logging.info("Successful serial connection with device %s", port.device)
            except:
                logging.error("Failed serial connection with device %s", port.device)
                pass
        time.sleep(1)


def main():
    timestamp = time.time_ns()
    with module_lock:
        for module in modules[:]:
            try:
                module.reset_input_buffer()
                module.reset_output_buffer()
                module.write(COMMANDS["READ_ALL"]())
                module.flush()
                logging.info("Sent command: %s", COMMANDS["READ_ALL"]())

                if module.in_waiting > 0:
                    res = module.readline()
                else:
                    modules.remove(module)
                    logging.error("Timed out waiting for ESP32 response.")
                    continue
                
                logging.info("Received message %s", res)
                data = json.loads(res.decode().strip())
                data["timestamp"] = timestamp
                logging.info(data)
            except serial.SerialException as e:
                logging.error("Serial error: %s", e)
            except JSONDecodeError as e:
                logging.error("Error decoding response from %s: %s", module.port, e)
                module.flush()
            except Exception as e:
                logging.error(e)
    time.sleep(1)


if __name__ == "__main__":
    reconnect_modules_thread = threading.Thread(target=reconnect_modules, daemon=True)
    try:
        reconnect_modules_thread.start()
        while True:
            main()
    except KeyboardInterrupt:
        logging.info("Exiting the program...")
    finally:
        stop_event.set()
        reconnect_modules_thread.join()


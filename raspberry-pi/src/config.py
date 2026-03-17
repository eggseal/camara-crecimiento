import logging
import os

from dotenv import load_dotenv

load_dotenv()

STREAM_SERVER_URL = os.environ["STREAM_SERVER_URL"]
STREAM_SERVER_PORT = os.environ["STREAM_SERVER_PORT"]
STREAM_DEVICE1 = int(os.environ["STREAM_DEVICE1"] or -1)
STREAM_DEVICE2 = int(os.environ["STREAM_DEVICE2"] or -1)
MODULE_DEVICE1 = os.environ["MODULE_DEVICE1"] 
MODULE_DEVICE2 = os.environ["MODULE_DEVICE2"] 

WIFI_PORT = int(os.environ["WIFI_PORT"])

logging.basicConfig(
    format=(
        "\033[90m%(asctime)s\033[0m [\033[36m%(levelname)s\033[0m] [\033[33m%(module)s::%(funcName)s\033[0m] %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

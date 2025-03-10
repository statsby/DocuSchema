import json
import os
import sys
from loguru import logger
import traceback

LOG_FILE = os.getenv("LOG_FILE", os.path.join(os.path.dirname(__file__), "log.log"))

def serializer(record):
    return json.dumps({
        "time": record["time"].isoformat(),
        "level": record["level"].name,
        "file": record["file"].name,
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        **record["extra"],
    })

def add_traceback(record):
    if record["level"].name.lower() in ("error", "critical") and record["extra"].get("with_traceback", False):
        record["extra"]["traceback"] = traceback.format_exc() if sys.exc_info()[0] else "No traceback available"


def sink_function(message):
    try:
        serialized = serializer(message.record)
        print(serialized, file=sys.stdout)
        if message.record["level"].name.lower() in ("error", "critical"):
            print(serialized, file=sys.stderr)
    except Exception as e:
        print(f"Logging Error: {e}", file=sys.stderr)

def setup_logger(log_level="INFO"):
    logger.remove()
    logger.patch(add_traceback)
    logger.add(sink_function, level=log_level)
    logger.add(LOG_FILE, 
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}", 
               rotation="2 week", 
               retention="30 days", 
               level=log_level)
    return logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = setup_logger(LOG_LEVEL)

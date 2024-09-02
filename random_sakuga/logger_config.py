import logging
import logging.handlers


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler_format = logging.Formatter(
    "%(levelname)s<%(asctime)s>%(module)s - %(funcName)s - %(lineno)d - %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
strream_handler_format = logging.Formatter("%(levelname)s - %(module)s - %(message)s")

file_handler = logging.handlers.RotatingFileHandler(
    "RandomSakuga.log", maxBytes=51200, backupCount=2
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_handler_format)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(strream_handler_format)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

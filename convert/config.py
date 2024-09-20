import os
import logging

db_location = os.environ["DB_LOCATION"]
lib_local = os.environ["LIB_LOCAL"]
lib_remote = os.environ["LIB_REMOTE"]
ext_local = os.environ["EXT_LOCAL"]
ext_remote = os.environ["EXT_REMOTE"]
ffmpeg_target = os.environ["FFMPEG_TARGET"]
log_level = os.environ["LOG_LEVEL"]
match (log_level):
    case 50:
        log_level = logging.CRITICAL

    case 40:
        log_level = logging.ERROR

    case 30:
        log_level = logging.WARNING

    case 20:
        log_level = logging.INFO

    case 10:
        log_level = logging.DEBUG

    case 0:
        log_level = logging.NOTSET

    case _:
        log_level = logging.INFO

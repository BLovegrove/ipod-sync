import os
import logging

db_location = os.environ["DB_LOCATION"]
lib_local = os.environ["LIB_LOCAL"]
lib_remote = os.environ["LIB_REMOTE"]
ext_local = os.environ["EXT_LOCAL"]
ext_remote = os.environ["EXT_REMOTE"]
ffmpeg_target = os.environ["FFMPEG_TARGET"]
log_level = os.environ["LOG_LEVEL"] if os.environ["LOG_LEVEL"] else logging.INFO

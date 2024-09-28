import os
import logging
import sys
from pathlib import Path

# use this when testing outside a docker environment. run like: python -m convert --test
if sys.argv[1] == "--test" or sys.argv[1] == "-t":
    os.environ["DB_LOCATION"] = "./testing/db.sqlite"
    os.environ["LIB_IMPORT"] = "./testing/import"
    os.environ["LIB_EXPORT"] = "./testing/export"
    os.environ["EXT_IMPORT"] = ".flac"
    os.environ["LOG_LEVEL"] = "20"

# where does the database file go?
db_location = os.environ["DB_LOCATION"]
Path(db_location).parent.mkdir(parents=True, exist_ok=True)

# import files from here
lib_import = os.environ["LIB_IMPORT"]
Path(lib_import).mkdir(parents=True, exist_ok=True)

# expport files into here
lib_export = os.environ["LIB_EXPORT"]
Path(lib_export).mkdir(parents=True, exist_ok=True)

# file extension being targeted for import files. e.g. '.mp3' - THE . IS IMPORTANT
ext_import = os.environ["EXT_IMPORT"]

# log level - info should be used in most cases.
log_level = int(os.environ["LOG_LEVEL"]) if os.environ["LOG_LEVEL"] else 20
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

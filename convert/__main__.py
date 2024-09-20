import sys
import logging.handlers
import subprocess
import sqlite3 as sql
import time
from convert import config as cfg
import os
from pathlib import Path
import logging
import coloredlogs

coloredlogs.install()
logger = logging.getLogger(__name__)

logging.basicConfig(
    encoding="utf-8",
    level=cfg.log_level,
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

file_handler = logging.handlers.RotatingFileHandler(
    "/database/run.log", maxBytes=1073741824, backupCount=10, encoding="utf-8"
)
# console_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(console_handler)
logger.addHandler(file_handler)


class MusicDB:
    def __init__(self) -> None:
        logger.info("Starting database...")
        db_path = cfg.db_location

        self.connection = sql.connect(db_path)
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS uploads (file_name TEXT PRIMARY KEY,synced BOOLEAN)"
        )

        self.commit()

    def commit(self):
        self.connection.commit()

    def kill(self):
        self.cursor.close()
        self.connection.close()

    def add_track(self, filename: str):
        filename_clean = filename.replace("'", "").replace('"', "").replace("`", "")
        query = f'INSERT INTO uploads(file_name,synced) VALUES ("{filename_clean}",1)'
        self.cursor.execute(query)

    def get_tracks(self):
        tracks = []
        self.cursor.execute("SELECT * FROM uploads")
        result = self.cursor.fetchall()

        for track in result:
            tracks.append(track)

        return tracks

    def track_exists(self, filename: str):
        exists = False
        try:
            filename_clean = filename.replace("'", "").replace('"', "").replace("`", "")
            query = f'SELECT * FROM uploads WHERE file_name="{filename_clean}"'
            self.cursor.execute(query)
            result = self.cursor.fetchone()[0]
            if result:
                exists = True
        except Exception as e:
            pass

        return exists


def upload(db: MusicDB):
    skipped = []
    # file names of tracks to upload
    to_upload = []
    # unique names of tracks (album_trackfile)
    synced = []

    logger.info("Scanning files to upload...")
    for current_dir, folders, files in os.walk(cfg.lib_local):
        for file in files:
            file_path = os.path.abspath(os.path.join(current_dir, file))
            album_name = Path(file_path).parent.name
            unique_name = f"{album_name}_{file}"
            if (
                file.endswith(cfg.ext_local)
                and db.track_exists(unique_name) == False
                and unique_name not in synced
            ):
                to_upload.append(file_path)
                synced.append(unique_name)
            else:
                logger.info(f"Track {file} already processed: skipping...")
                skipped.append(file_path)

    logger.info(
        f"[{len(skipped) + len(to_upload)}] Tracks found. [{len(skipped)}] Already in destination system. Processing remaining [{len(to_upload)}] files..."
    )
    for file in to_upload:
        logger.info(
            f"Starting transcode for track #[{to_upload.index(file) + 1}] of #[{len(to_upload)}]: [{Path(file).parent.name}]/[{os.path.basename(file)}]."
        )
        codec = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=codec_name",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                file,
            ]
        )

        if cfg.ext_local.replace(".", "") in str(codec):
            album_name = Path(file).parent.name
            os.makedirs(os.path.join(cfg.lib_remote, album_name), exist_ok=True)

            target = os.path.join(
                cfg.lib_remote + f"/{album_name}",
                os.path.basename(file.replace(cfg.ext_local, cfg.ext_remote)),
            )
            attempts = 0
            while True:
                try:
                    subprocess.call(
                        [
                            "ffmpeg",
                            "-i",
                            file,
                            "-c:a",
                            cfg.ffmpeg_target,
                            "-c:v",
                            "copy",
                            target,
                        ]
                    )
                    attempts += 1
                    break
                except:
                    # too many failed attempts
                    if attempts >= 10:
                        logger.critical(
                            f"TRANSCODE_CRITICAL. Transcoder failed to process track [{target}] 10 times in succession. Something is likely wrong with its file/format."
                        )

                    # clear file for next attempt
                    if os.path.exists(target):
                        os.remove(target)

                    # transcode cooldown
                    logger.warning(
                        f"TRANSCODE_FAILURE. Transcoder failed while processing track [{target}]."
                    )
                    time.sleep(60)

            logger.info(
                f"TRANSCODE_SUCCESS. Track [{target}] is being sent to your configured destination."
            )
            db.add_track(synced[to_upload.index(file)])
            db.commit()


def main():
    db = MusicDB()
    upload(db)
    db.kill()
    logger.info("Done! Enjoy your music")


if __name__ == "__main__":
    main()

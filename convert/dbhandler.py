import sqlite3 as sql
import os


class MusicDB:
    def __init__(self) -> None:
        db_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "music.sqlite"
        )

        self.connection = sql.connect(db_path)
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS transferred (track_name TEXT PRIMARY KEY, track_path TEXT NOT NULL)"
        )

        self.connection.commit()

    def kill(self):
        self.cursor.close()
        self.connection.close()

    def add_track(self, table: str, name: str, path):
        self.cursor.execute(f"INSERT INTO {table} VALUES({name},{path})")




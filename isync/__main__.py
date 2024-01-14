import subprocess
import os
import config as cfg
import glob


def is_locked():
    locked = os.path.exists(f"{cfg.local_library}/{cfg.lockfile}")
    if locked:
        print(cfg.lock_warning)
        return True
    else:
        return False


def set_locked():
    f = open(f"{cfg.local_library}/{cfg.lockfile}", "a")
    f.write("")
    f.close()


def set_unlocked():
    os.remove(f"{cfg.local_library}/{cfg.lockfile}")


def to_flac():
    if set_locked():
        return

    set_locked()
    subprocess.call(["fdfind", "--extension", "m4a", "--exec", "mv", "{}", "{.}.flac"])
    set_unlocked()


def to_alac():
    if set_locked():
        return

    set_locked()
    subprocess.call(["fdfind", "--extension", "flac", "--exec", "mv", "{}", "{.}.m4a"])
    set_unlocked()


def update_library():
    if is_locked():
        return

    set_locked()
    subprocess.call(
        [
            "rclone",
            "copy",
            cfg.remote_library,
            cfg.local_library,
            "--ignore-existing",
            "--progress",
        ]
    )
    set_unlocked()


def process_audio():
    if is_locked():
        return

    queue: list[str] = []
    strip_cover = False

    set_locked()
    for current_dir, subdirs, files in os.walk(cfg.local_library):
        if "library.lock" in files:
            continue

        if files != []:
            if not os.path.exists(os.path.join(current_dir, "folder.jpg")):
                strip_cover = True

        for file in files:
            if file.endswith(".jpg"):
                continue

            file_path = os.path.abspath(os.path.join(current_dir, file))
            if strip_cover:
                subprocess.call(
                    [
                        "ffmpeg",
                        "-i",
                        file_path,
                        "-an",
                        "-c:v",
                        "copy",
                        os.path.join(current_dir, "folder_tmp.jpg"),
                    ]
                )
                subprocess.call(
                    [
                        "convert",
                        os.path.join(current_dir, "folder_tmp.jpg"),
                        "-resize",
                        "200x200",
                        "-interlace",
                        "None",
                        os.path.join(current_dir, "folder.jpg"),
                    ]
                )
                os.remove(os.path.join(current_dir, "folder_tmp.jpg"))
                # input("stopping after image strip")
                strip_cover = False

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
                    file_path,
                ]
            )
            if codec == "flac":
                queue.append(file_path)

    for file in queue:
        # transcode from flac -> alac, keeping .flac ext for rclone sake
        subprocess.call(
            [
                "ffmpeg",
                "-i",
                file,
                "-c:a",
                "alac",
                "-c:v",
                "copy",
                file.replace(".flac", ".m4a"),
            ]
        )
        os.remove(file)
    set_unlocked()


def main():
    to_flac()
    update_library()
    process_audio()
    to_alac()


if __name__ == "__main__":
    main()

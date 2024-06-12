import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script_to_run = script

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.run_script_async(event.src_path)

    def run_script_async(self, file_path):
        subprocess.Popen(['python', self.script_to_run, file_path])


if __name__ == "__main__":
    directory_to_watch = "detections"
    script_to_run = "movement_analysis.py"

    event_handler = FileCreatedHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False)

    observer.start()
    print(f"Monitoring directory: {directory_to_watch}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopping monitoring...")

    observer.join()

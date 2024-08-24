import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from multiprocessing import Process, Queue


class FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, script, queue):
        self.script_to_run = script
        self.queue = queue

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.queue.put(event.src_path)


def worker(queue, script):
    while True:
        file_path = queue.get()
        if file_path is None:
            break
        print(f"Processing file: {file_path}")
        subprocess.run(['python', script, file_path])


if __name__ == "__main__":
    directory_to_watch = "desktop_app/detections"
    script_to_run = "desktop_app/movement_analysis.py"

    queue = Queue()
    event_handler = FileCreatedHandler(script_to_run, queue)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False)

    process = Process(target=worker, args=(queue, script_to_run))
    process.start()

    observer.start()
    print(f"Monitoring directory: {directory_to_watch}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopping monitoring...")

    queue.put(None)
    process.join()

    observer.join()

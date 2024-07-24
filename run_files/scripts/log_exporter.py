import json
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Elasticsearch settings
ELASTICSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "system-logs"
MAX_RETRIES = 5
INITIAL_BACKOFF = 10  # in seconds

def send_log_to_elasticsearch(log_entry, retries=0):
    url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_doc"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(log_entry))
        if response.status_code == 201:
            print(f"Log entry indexed successfully: {log_entry}")
        else:
            print(f"Failed to index log entry: {log_entry}, response: {response.text}")
    except requests.exceptions.RequestException as e:
        if retries < MAX_RETRIES:
            backoff_time = INITIAL_BACKOFF * (2 ** retries)
            print(f"Elasticsearch is not available. Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            send_log_to_elasticsearch(log_entry, retries + 1)
        else:
            print(f"Failed to index log entry after {MAX_RETRIES} retries: {log_entry}. Error: {e}")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "r")
        # Go to the end of the file
        self.file.seek(0, 2)

    def on_modified(self, event):
        if event.src_path == self.file_path:
            self.read_new_lines()

    def read_new_lines(self):
        for line in self.file:
            log_entry = {
                "@timestamp": datetime.now().isoformat(),
                "message": line.strip()
            }
            send_log_to_elasticsearch(log_entry)

if __name__ == "__main__":
    # Path to the system log file
    log_file_path = "/var/log/syslog"

    event_handler = LogFileHandler(log_file_path)
    observer = Observer()
    observer.schedule(event_handler, path=log_file_path, recursive=False)
    observer.start()

    try:
        while True:
            # Keep the script running
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

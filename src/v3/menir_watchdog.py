"""
Menir Watchdog Service
Horizon 4 - Omnipresent Automation

Monitors a specified folder (e.g., a shared Google Drive or Dropbox path).
When a new file is detected, it automatically bridges into
the Menir 4-Stage Ingestion Pipeline without user interaction.
"""

import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from src.v3.ingestion_engine import IngestionPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

logger = logging.getLogger("MenirWatchdog")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - [WATCHDOG] - %(message)s"))
logger.addHandler(handler)

class MenirIngestionHandler(FileSystemEventHandler):
    def __init__(self, target_project: str):
        super().__init__()
        self.project = target_project
        if PIPELINE_AVAILABLE:
            self.pipeline = IngestionPipeline()
        else:
            self.pipeline = None

    def on_created(self, event):
        if event.is_directory:
            return
            
        file_ext = os.path.splitext(event.src_path)[1].lower()
        if file_ext in ['.txt', '.pdf', '.csv', '.md']:
            logger.info(f"📥 New file detected: {event.src_path}")
            self.trigger_pipeline(event.src_path)
            
    def trigger_pipeline(self, filepath: str):
        if not self.pipeline:
            logger.error("V3 Ingestion Pipeline not available. Skipping ingestion.")
            return
            
        logger.info(f"⚙️ Auto-Ingesting {os.path.basename(filepath)} into Project: {self.project}...")
        try:
            self.pipeline.run(filepath, self.project)
            logger.info(f"✅ Auto-Ingestion Complete for {os.path.basename(filepath)}")
        except Exception as e:
            logger.error(f"❌ Auto-Ingestion Failed: {e}")

def start_watchdog(path_to_watch: str, project_name: str = "Automated_DropBox"):
    logger.info(f"👀 Menir Auto-Ingestor watching directory: {path_to_watch}")
    
    event_handler = MenirIngestionHandler(target_project=project_name)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Watchdog shutting down...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Create the landing pad if it doesn't exist
    watch_dir = os.path.join(os.getcwd(), "staging", "auto_ingest_drop")
    os.makedirs(watch_dir, exist_ok=True)
    
    # Normally this runs as a background daemon
    start_watchdog(watch_dir, project_name="DRIVE_SYNC_001")

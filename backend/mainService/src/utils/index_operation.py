import json
import threading
import os
import time
from datetime import datetime, timezone
from src.config.log_config import setup_logging

INDEX_DICT_FILE = 'index_dict.json'
INDEX_TEMP_FILE = 'index_dict.tmp'  # the temp file

# In-memory dictionary to store index creation times.
index_dict = {}

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)


def add_index_to_memory(index_name: str):
    """Add a new index creation event to the in-memory dictionary."""
    creation_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H")
    indexes: list = index_dict.get(creation_time, [])
    indexes.append(index_name)
    index_dict[creation_time] = indexes
    logger.info(f"Added {index_name} at {creation_time}")


def flush_index_dict_periodically(interval: int = 60):
    """Flush the in-memory dictionary to disk every `interval` seconds."""
    while True:
        time.sleep(interval)
        try:
            with open(INDEX_TEMP_FILE, 'w') as f:
                json.dump(index_dict, f)
            os.replace(INDEX_TEMP_FILE, INDEX_DICT_FILE)
            index_dict.clear()
            logger.info(f"Flushed {len(index_dict)} indexes to disk.")
        except Exception as e:
            logger.exception(f"Error flushing index dict: {e}")


def start():
    # Start the background flushing thread (as a daemon so it doesn't block
    # program exit)
    flush_thread = threading.Thread(
        target=flush_index_dict_periodically, args=(
            180,), daemon=True)
    flush_thread.start()


# Example usage when creating an index:
if __name__ == "__main__":
    # Whenever you create a new index, just call:
    new_index_name = "example_file.pdf"
    add_index_to_memory(new_index_name)

    # Your main process can continue doing other tasks...
    # For demonstration, keep the script running so the background thread
    # works.
    while True:
        time.sleep(10)

import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
from pinecone import PineconeAsyncio as Pinecone
from collections import defaultdict
from src.config.log_config import setup_logging

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)

# Initialize Pinecone with your API key and environment


INDEX_DICT_FILE = 'index_dict.json'
THRESHOLD_HOURS = 2  # Delete indexes older than 2 hours


def load_index_dict() -> Dict[str, List[str]]:
    """Load the index dictionary from the JSON file.    
    Returns:
        Dict[str, List[str]]: Dictionary mapping hourly timestamps to lists of index names.
        Returns defaultdict with empty list as default if file doesn't exist.
    """
    if os.path.exists(INDEX_DICT_FILE):
        with open(INDEX_DICT_FILE, 'r') as f:
            return defaultdict(list, json.load(f))
    return defaultdict(list)


def save_index_dict(index_dict: Dict[str, List[str]]) -> None:
    """Save the index dictionary to the JSON file.
    
    Args:
        index_dict (Dict[str, List[str]]): Dictionary mapping timestamps to lists of index names.
    """
    with open(INDEX_DICT_FILE, 'w') as f:
        json.dump(dict(index_dict), f)  # Convert defaultdict to regular dict for JSON serialization


async def delete_index(index_name: str, pc:Pinecone) -> Tuple[str, bool, str]:
    """Delete a single Pinecone index.
    
    Args:
        index_name (str): Name of the index to delete
        
    Returns:
        Tuple[str, bool, str]: Tuple containing:
            - Index name
            - Boolean indicating success/failure
            - Error message if failure, empty string if success
    """
    
    try:
        await pc.delete_index(index_name)
        return index_name, True, ""
    except Exception as e:
        return index_name, False, str(e)


async def delete_old_indexes(threshold_hours: int = THRESHOLD_HOURS) -> None:
    """Asynchronously delete Pinecone indexes older than the threshold.
    
    This function loads the index dictionary, identifies indexes from timestamps older
    than the threshold, and deletes them concurrently using asyncio.gather.
    
    Args:
        threshold_hours (int, optional): Age threshold in hours. Defaults to THRESHOLD_HOURS.
    """
    API_KEY = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=API_KEY)
    
    index_dict = load_index_dict()
    now = datetime.now(timezone.utc)
    updated_dict = defaultdict(list)
    indexes_to_delete = []
    
    # Process each timestamp and its indexes
    for timestamp_str, index_list in index_dict.items():
        try:
            creation_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H").replace(tzinfo=timezone.utc)
            print("creeation_time:", creation_time)
            if now - creation_time >= timedelta(minutes=threshold_hours):
                # Add all indexes from this timestamp to deletion list
                indexes_to_delete.extend(index_list)
            else:
                # Keep indexes from recent timestamps
                updated_dict[timestamp_str] = index_list
        except ValueError as e:
            logger.exception(f"Error parsing timestamp '{timestamp_str}': {e}")
            # Keep entries with invalid timestamps for manual review
            updated_dict[timestamp_str] = index_list
    
    if indexes_to_delete:
        # Execute deletions concurrently
        results = await asyncio.gather(
            *[delete_index(index_name, pc=pc) for index_name in indexes_to_delete],
            return_exceptions=True
        )        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Unexpected error during deletion: {result}")
                continue
                
            index_name, success, error = result
            if success:
                logger.info(f"Successfully deleted index '{index_name}'")
            else:
                print(f"Failed to delete index '{index_name}': {error}")
                # For failed deletions, keep them in their original timestamp bucket
                # This requires finding the original timestamp
                for timestamp_str, indexes in index_dict.items():
                    if index_name in indexes:
                        updated_dict[timestamp_str].append(index_name)
                        break
    
    save_index_dict(updated_dict)
    print("Deletion job complete. Remaining indexes by timestamp:", 
          {ts: indexes for ts, indexes in updated_dict.items() if indexes})
    await pc.close()

if __name__ == "__main__":
    asyncio.run(delete_old_indexes())
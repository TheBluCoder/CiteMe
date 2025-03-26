#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")/.."

# Run the cleanup script
python scripts/delete_stale_data.py 
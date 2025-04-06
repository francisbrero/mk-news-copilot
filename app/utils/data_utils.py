import json
import os
from typing import List, Dict, Any
from pathlib import Path
from threading import Lock

# File paths
DATA_DIR = Path("data")
NEWS_FILE = DATA_DIR / "news.json"
COMPANIES_FILE = DATA_DIR / "companies.json"
SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.json"

# Thread-safe file operations
file_locks = {
    NEWS_FILE: Lock(),
    COMPANIES_FILE: Lock(),
    SUBSCRIPTIONS_FILE: Lock()
}

def ensure_data_files():
    """Create data directory and empty JSON files if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    
    empty_json = {"items": []}
    for file_path in [NEWS_FILE, COMPANIES_FILE, SUBSCRIPTIONS_FILE]:
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump(empty_json, f)

def read_json_file(file_path: Path) -> Dict[str, List[Any]]:
    """Thread-safe read from JSON file."""
    with file_locks[file_path]:
        if not file_path.exists():
            return {"items": []}
        with open(file_path, 'r') as f:
            return json.load(f)

def write_json_file(file_path: Path, data: Dict[str, List[Any]]) -> None:
    """Thread-safe write to JSON file."""
    with file_locks[file_path]:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

def append_item(file_path: Path, item: Dict[str, Any]) -> None:
    """Thread-safe append item to JSON file."""
    with file_locks[file_path]:
        data = read_json_file(file_path)
        data["items"].append(item)
        write_json_file(file_path, data)

# Initialize data files
ensure_data_files()
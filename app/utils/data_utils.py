import json
import os
from typing import List, Dict, Any
from pathlib import Path
from threading import Lock
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from fastapi import HTTPException

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

def ensure_data_dir():
    """Ensure the data directory exists and create it if it doesn't."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir

def load_json_file(filename: str) -> Dict[str, List[Dict[Any, Any]]]:
    """Load data from a JSON file. Create empty structure if file doesn't exist."""
    filepath = ensure_data_dir() / filename
    if not filepath.exists():
        return {"items": []}
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        if not isinstance(data, dict) or 'items' not in data:
            return {"items": []}
        return data

def save_json_file(filename: str, data: Dict[str, List[Dict[Any, Any]]]) -> None:
    """Save data to a JSON file atomically."""
    if not isinstance(data, dict) or 'items' not in data:
        data = {"items": []}
    
    filepath = ensure_data_dir() / filename
    temp_filepath = filepath.with_suffix('.tmp')
    
    # First write to a temporary file
    with open(temp_filepath, 'w') as f:
        json.dump(data, f, indent=2, default=json_serialize)
    
    # Then rename it to the target file (atomic operation)
    os.replace(temp_filepath, filepath)

def json_serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, HttpUrl):
        return str(obj)
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f"Type {type(obj)} not serializable")

def ensure_data_files():
    """Create data directory and empty JSON files if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    
    empty_json = {"items": []}
    for file_path in [NEWS_FILE, COMPANIES_FILE, SUBSCRIPTIONS_FILE]:
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump(empty_json, f)

def read_json_file(filename: str) -> List[Dict[str, Any]]:
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {filename}: {str(e)}")

def write_json_file(filename: str, data: List[Dict[str, Any]]) -> None:
    filepath = os.path.join(DATA_DIR, filename)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing to {filename}: {str(e)}")

def get_news() -> List[Dict[str, Any]]:
    return read_json_file("news.json")

def get_companies() -> List[Dict[str, Any]]:
    return read_json_file("companies.json")

def get_subscriptions() -> List[Dict[str, Any]]:
    return read_json_file("subscriptions.json")

def save_subscriptions(subscriptions: List[Dict[str, Any]]) -> None:
    write_json_file("subscriptions.json", subscriptions)

def append_item(file_path: Path, item: Dict[str, Any]) -> None:
    """Thread-safe append item to JSON file."""
    with file_locks[file_path]:
        data = read_json_file(file_path)
        data["items"].append(item)
        write_json_file(file_path, data)

# Initialize data files
ensure_data_files() 

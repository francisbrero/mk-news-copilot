import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path('data')

def ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(exist_ok=True)

def read_json_file(filename: str) -> List[Dict[str, Any]]:
    """Read data from a JSON file atomically."""
    file_path = DATA_DIR / filename
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_json_file(filename: str, data: List[Dict[str, Any]]) -> None:
    """Write data to a JSON file atomically."""
    file_path = DATA_DIR / filename
    temp_path = file_path.with_suffix('.tmp')
    
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    temp_path.replace(file_path)

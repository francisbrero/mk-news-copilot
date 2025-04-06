import json
from pathlib import Path
from typing import Any, Dict, List, Union

DATA_DIR = Path('data')

def read_json_file(filename: str) -> List[Dict]:
    """
    Read data from a JSON file in the data directory.
    Returns empty list if file doesn't exist or is invalid.
    """
    file_path = DATA_DIR / filename
    try:
        if not file_path.exists():
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_json_file(filename: str, data: Any) -> None:
    """
    Write data to a JSON file in the data directory.
    Creates directories if they don't exist.
    """
    file_path = DATA_DIR / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to a temporary file first
    temp_path = file_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Then atomically replace the target file
    temp_path.replace(file_path)
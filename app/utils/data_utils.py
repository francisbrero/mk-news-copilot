import json
import os
from typing import List, Dict, Any, Union
from pathlib import Path
from threading import Lock
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from fastapi import HTTPException
import uuid
from passlib.hash import bcrypt

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

def parse_date(date_str: str) -> datetime:
    """Parse various date formats into datetime objects."""
    try:
        # Try parsing RFC 2822 format (e.g. 'Mon, 07 Apr 2025 14:56:27 +0000')
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str)
        except:
            raise ValueError(f"Unable to parse date: {date_str}")

def read_json_file(filename: str) -> List[Dict[str, Any]]:
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            # If this is news.json, ensure each article has an ID and proper date format
            if filename == "news.json":
                for article in data:
                    if "id" not in article:
                        article["id"] = str(uuid.uuid4())
                    if "published_at" in article:
                        try:
                            # Convert to ISO format string
                            article["published_at"] = parse_date(article["published_at"]).isoformat()
                        except ValueError:
                            # If date parsing fails, use current time
                            article["published_at"] = datetime.utcnow().isoformat()
            
            return data
    except json.JSONDecodeError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {filename}: {str(e)}")

def serialize_json(obj: Any) -> Any:
    """Custom JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, HttpUrl):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def write_json_file(filename: str, data: List[Dict[str, Any]]) -> None:
    filepath = os.path.join(DATA_DIR, filename)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=serialize_json)
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

def save_companies(companies: List[Dict[str, Any]]) -> None:
    write_json_file("companies.json", companies)

def add_company(company: Dict[str, Any]) -> Dict[str, Any]:
    companies = get_companies()
    
    # Check if company with same name already exists
    if any(c["name"].lower() == company["name"].lower() for c in companies):
        raise HTTPException(status_code=400, detail=f"Company with name '{company['name']}' already exists")
    
    # Ensure company has an ID
    if "id" not in company:
        company["id"] = str(uuid.uuid4())
    
    companies.append(company)
    save_companies(companies)
    return company

def append_item(file_path: Path, item: Dict[str, Any]) -> None:
    """Thread-safe append item to JSON file."""
    with file_locks[file_path]:
        data = read_json_file(file_path)
        data["items"].append(item)
        write_json_file(file_path, data)

def get_users() -> List[Dict]:
    """Get all users from users.json"""
    return read_json_file('users.json')

def get_user_by_id(user_id: str) -> Union[Dict, None]:
    """Get a user by ID"""
    users = get_users()
    return next((u for u in users if u['id'] == user_id), None)

def get_user_by_email(email: str) -> Union[Dict, None]:
    """Get a user by email"""
    users = get_users()
    return next((u for u in users if u['email'] == email), None)

def create_user(user_data: Dict) -> Dict:
    """Create a new user"""
    users = get_users()
    
    # Check if email already exists
    if get_user_by_email(user_data['email']):
        raise ValueError('Email already exists')
    
    # Hash password
    user_data['password'] = bcrypt.hash(user_data['password'])
    
    # Add metadata
    now = datetime.utcnow().isoformat()
    user = {
        **user_data,
        'id': str(uuid.uuid4()),
        'created_at': now,
        'updated_at': now
    }
    
    users.append(user)
    write_json_file('users.json', users)
    
    # Return user without password
    user_response = user.copy()
    del user_response['password']
    return user_response

def update_user(user_id: str, user_data: Dict) -> Union[Dict, None]:
    """Update a user"""
    users = get_users()
    user_idx = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
    
    if user_idx is None:
        return None
        
    # Update user data
    user = users[user_idx]
    if 'password' in user_data:
        user_data['password'] = bcrypt.hash(user_data['password'])
    
    user = {
        **user,
        **user_data,
        'updated_at': datetime.utcnow().isoformat()
    }
    users[user_idx] = user
    
    write_json_file('users.json', users)
    
    # Return user without password
    user_response = user.copy()
    del user_response['password']
    return user_response

def delete_user(user_id: str) -> bool:
    """Delete a user and their subscriptions"""
    users = get_users()
    user_idx = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
    
    if user_idx is None:
        return False
        
    # Delete user
    users.pop(user_idx)
    write_json_file('users.json', users)
    
    # Delete user's subscriptions
    subscriptions = read_json_file('subscriptions.json')
    subscriptions = [s for s in subscriptions if s['user_id'] != user_id]
    write_json_file('subscriptions.json', subscriptions)
    
    return True

# Initialize data files
ensure_data_files() 

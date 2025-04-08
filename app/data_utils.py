import json
from pathlib import Path
from typing import Any, Dict, List, Union
from datetime import datetime
import uuid
from passlib.hash import bcrypt

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
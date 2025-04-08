import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from pathlib import Path
import shutil
from app.utils.data_utils import set_data_dir
from datetime import datetime, timezone

client = TestClient(app)

# Mock data paths
TEST_DATA_DIR = Path("tests/test_data")

@pytest.fixture(autouse=True)
def setup_test_data():
    """Setup test data before each test"""
    # Set data directory to test data
    set_data_dir(TEST_DATA_DIR)
    
    # Create test directory
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create mock news data
    news_data = [
        {
            "id": "1",
            "title": "Test Article 1",
            "url": "http://test.com/1",
            "source": "Test Source",
            "published_at": "2024-03-20T10:00:00Z",
            "content": "This is the full content of test article 1",
            "companies": ["company1"],
            "topics": ["Fundraising"],
            "summary": "Test summary 1"
        }
    ]
    
    # Create mock companies data
    companies_data = [
        {
            "id": "company1",
            "name": "Test Company",
            "domain": "testcompany.com"
        }
    ]
    
    # Create mock subscriptions data
    current_time = datetime.now(timezone.utc).isoformat()
    subscriptions_data = [
        {
            "id": "sub1",
            "user_id": "user1",
            "company_ids": ["company1"],
            "topics": ["funding", "product"],
            "created_at": current_time,
            "updated_at": current_time
        }
    ]
    
    # Create mock users data
    mock_users = [
        {
            "id": "user1",
            "email": "test@example.com",
            "password": "hashedpassword123",
            "name": "Test User",
            "created_at": current_time,
            "updated_at": current_time
        }
    ]
    
    # Write test data to files
    (TEST_DATA_DIR / "news.json").write_text(json.dumps({"items": news_data}))
    (TEST_DATA_DIR / "companies.json").write_text(json.dumps({"items": companies_data}))
    (TEST_DATA_DIR / "subscriptions.json").write_text(json.dumps({"items": subscriptions_data}))
    (TEST_DATA_DIR / "users.json").write_text(json.dumps({"items": mock_users}))
    
    yield
    
    # Cleanup after tests
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    
    # Reset data directory to default
    set_data_dir("data")

def test_get_news():
    response = client.get("/news")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Article 1"

def test_get_news_with_company_filter():
    response = client.get("/news?company=company1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "company1" in data[0]["companies"]

def test_get_news_with_topic_filter():
    response = client.get("/news?topic=Fundraising")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "Fundraising" in data[0]["topics"]

def test_get_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Company"

def test_get_companies_with_name_filter():
    response = client.get("/companies?name=Test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "Test" in data[0]["name"]

def test_get_subscriptions():
    response = client.get("/subscriptions/user1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "sub1"
    assert data[0]["user_id"] == "user1"
    assert data[0]["company_ids"] == ["company1"]
    assert data[0]["topics"] == ["funding", "product"]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]

def test_add_subscription():
    response = client.post(
        "/subscriptions",
        json={
            "user_id": "user2",
            "company_ids": ["company2"],
            "topics": ["acquisition", "layoff"]
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["user_id"] == "user2"
    assert response.json()["company_ids"] == ["company2"]
    assert response.json()["topics"] == ["acquisition", "layoff"]

def test_remove_subscription():
    # First add a subscription
    response = client.post(
        "/subscriptions",
        json={
            "user_id": "user3",
            "company_ids": ["company3"],
            "topics": ["funding"]
        }
    )
    subscription_id = response.json()["id"]
    
    # Then remove it
    response = client.delete(f"/subscriptions/{subscription_id}")
    assert response.status_code == 200
    
    # Verify subscription was removed
    response = client.get("/subscriptions/user3")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_delete_subscriptions():
    response = client.delete("/subscriptions?user_id=user1")
    assert response.status_code == 200
    
    # Verify all subscriptions were removed
    response = client.get("/subscriptions/user1")
    data = response.json()
    assert len(data) == 0

def test_get_feed():
    response = client.get("/feed?user_id=user1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Article 1"

def test_create_user():
    payload = {
        "name": "New User",
        "email": "new@example.com",
        "password": "testpassword123"
    }
    response = client.post("/users", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "new@example.com"
    assert "password" not in data  # Password should not be returned
    assert "created_at" in data
    assert "updated_at" in data

def test_get_user():
    response = client.get("/users/user1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"

def test_update_user():
    payload = {
        "name": "Updated User",
        "email": "updated@example.com"
    }
    response = client.put("/users/user1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["email"] == "updated@example.com"

def test_delete_user():
    response = client.delete("/users/user1")
    assert response.status_code == 204
    
    # Verify user was deleted
    response = client.get("/users/user1")
    assert response.status_code == 404 
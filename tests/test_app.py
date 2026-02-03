import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    # Test signing up for an activity
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@mergington.edu for Chess Club" in data["message"]

    # Check if added to participants
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate():
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_success():
    # First add a participant
    client.post("/activities/Programming%20Class/signup?email=remove@mergington.edu")

    # Then remove
    response = client.delete("/activities/Programming%20Class/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered remove@mergington.edu from Programming Class" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "remove@mergington.edu" not in data["Programming Class"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_participant_not_found():
    response = client.delete("/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found in activity"
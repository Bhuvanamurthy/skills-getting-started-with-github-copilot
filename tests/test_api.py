"""
Tests for the High School Management System API
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect response, but TestClient follows redirects by default
    # Actually, let me check what happens
    assert "text/html" in response.headers.get("content-type", "")


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check that each activity has the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_successful():
    """Test successful signup for an activity"""
    # Use an activity that exists and has space
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Basketball Team" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Basketball Team"]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    """Test signup when already signed up"""
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")

    # Try to signup again
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_successful():
    """Test successful unregister from an activity"""
    # First signup
    client.post("/activities/Art%20Club/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Art%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]
    assert "Art Club" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Art Club"]["participants"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    """Test unregister when not signed up"""
    response = client.delete("/activities/Debate%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]
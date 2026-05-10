import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Copy of initial activities for resetting
initial_activities = activities.copy()

@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset the activities dictionary before each test."""
    global activities
    activities.clear()
    activities.update(initial_activities)

# Tests for GET /activities
def test_get_activities(client):
    """Test retrieving all activities."""
    # Arrange - No special setup needed, activities are initialized

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

# Tests for POST /activities/{activity_name}/signup
def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" == data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities_data = response.json()
    assert email in activities_data[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test signup when student is already signed up (duplicate)."""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" == data["detail"]

def test_signup_nonexistent_activity(client):
    """Test signup for a non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity_name = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

# Tests for DELETE /activities/{activity_name}/participants/{email}
def test_remove_participant_success(client):
    """Test successful removal of a participant."""
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity_name}" == data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities_data = response.json()
    assert email not in activities_data[activity_name]["participants"]

def test_remove_participant_nonexistent_activity(client):
    """Test removal from a non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity_name = "NonExistent Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

def test_remove_participant_not_signed_up(client):
    """Test removal when student is not signed up."""
    # Arrange
    email = "notsigned@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" == data["detail"]
from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    yield
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_root_redirects_to_static_index():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert isinstance(body["Chess Club"]["participants"], list)


def test_signup_creates_new_participant():
    # Arrange
    client = TestClient(app)
    activity = quote("Chess Club")
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_error():
    # Arrange
    client = TestClient(app)
    activity = quote("Chess Club")
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unregisters_student():
    # Arrange
    client = TestClient(app)
    activity = quote("Chess Club")
    email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]

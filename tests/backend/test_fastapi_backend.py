from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def reset_activities():
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
        "Soccer Team": {
            "description": "Practice teamwork and compete in friendly soccer matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"],
        },
        "Swimming Club": {
            "description": "Develop swimming skills and train for lap races",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["natalie@mergington.edu", "alex@mergington.edu"],
        },
        "Art Workshop": {
            "description": "Explore visual art techniques and create original pieces",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["harper@mergington.edu", "liam@mergington.edu"],
        },
        "Drama Club": {
            "description": "Rehearse scenes and prepare performances for the school stage",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"],
        },
        "Science Olympiad": {
            "description": "Participate in science competitions and hands-on experiments",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["zoe@mergington.edu", "noah@mergington.edu"],
        },
        "Debate Team": {
            "description": "Build critical thinking and public speaking skills",
            "schedule": "Mondays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 14,
            "participants": ["sophia@mergington.edu", "jack@mergington.edu"],
        },
    }

    activities.clear()
    activities.update(deepcopy(original_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_new_participant():
    reset_activities()
    email = "new.student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    reset_activities()

    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_returns_404_for_unknown_activity():
    reset_activities()

    response = client.post("/activities/Unknown Club/signup", params={"email": "alice@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant():
    reset_activities()

    response = client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}

    activities_response = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities_response["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant():
    reset_activities()

    response = client.delete("/activities/Chess Club/signup", params={"email": "missing@mergington.edu"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up"}

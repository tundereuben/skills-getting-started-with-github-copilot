from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_updates_activity_state():
    email = f"{uuid4().hex}@example.com"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200

    activities = client.get("/activities").json()

    assert email in activities["Chess Club"]["participants"]

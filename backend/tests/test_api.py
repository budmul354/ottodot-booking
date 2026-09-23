from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import Parent, Student, TrialClass


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session.begin() as db:
        parent = Parent(name="API Parent", email="api@example.com")
        db.add_all([parent, Student(name="API Child", parent=parent), TrialClass(title="API Trial", starts_at=datetime.now(timezone.utc), capacity=1)])
    def override_db():
        with Session() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_api_booking_payment_and_roster_flow(client):
    student = client.get("/students").json()[0]
    trial_class = client.get("/trial-classes").json()[0]
    booking = client.post("/bookings", json={"student_id": student["id"], "trial_class_id": trial_class["id"]})
    assert booking.status_code == 201
    payment = client.post(f"/bookings/{booking.json()['booking_id']}/payment", json={"result": "success"})
    assert payment.json()["booking_status"] == "confirmed"
    roster = client.get(f"/bookings/trial-classes/{trial_class['id']}/roster")
    assert roster.json()["students"][0]["name"] == "API Child"


def test_api_rejects_invalid_payment_result(client):
    response = client.post("/bookings/1/payment", json={"result": "maybe"})
    assert response.status_code == 422


def test_health_and_metrics_are_available(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert "booking_created_total" in client.get("/metrics").json()

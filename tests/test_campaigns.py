from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_campaign_success():
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/campaigns/",
        json={"title": "School Robotics Team", "goal": 1200, "deadline": deadline},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "School Robotics Team"
    assert body["pledged"] == 0
    assert body["status"] == "active"


def test_reject_overfunding():
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    campaign = client.post(
        "/campaigns/",
        json={"title": "Music Camp", "goal": 1000, "deadline": deadline},
    ).json()
    campaign_id = campaign["id"]
    ok = client.post(f"/campaigns/{campaign_id}/pledge", json={"user_name": "ana", "amount": 800})
    assert ok.status_code == 201
    reject = client.post(f"/campaigns/{campaign_id}/pledge", json={"user_name": "sam", "amount": 250})
    assert reject.status_code == 400
    assert "overfund" in reject.json()["detail"].lower()


def test_refund_expired_unfunded_campaign():
    deadline = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    campaign = client.post(
        "/campaigns/",
        json={"title": "Old Campaign", "goal": 1000, "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()},
    ).json()
    campaign_id = campaign["id"]
    pledge = client.post(f"/campaigns/{campaign_id}/pledge", json={"user_name": "nina", "amount": 200})
    assert pledge.status_code == 201

    db = TestingSessionLocal()
    try:
        row = db.execute(
            text("UPDATE campaigns SET deadline = :deadline WHERE id = :id"),
            {"deadline": datetime.fromisoformat(deadline).replace(tzinfo=None), "id": campaign_id},
        )
        db.commit()
        assert row.rowcount == 1
    finally:
        db.close()

    refund = client.post(f"/campaigns/{campaign_id}/refunds")
    assert refund.status_code == 200
    assert refund.json()["total_refunded"] == 200


def test_cannot_refund_funded_campaign():
    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    campaign = client.post(
        "/campaigns/",
        json={"title": "Sports Kits", "goal": 300, "deadline": deadline},
    ).json()
    campaign_id = campaign["id"]
    pledge = client.post(f"/campaigns/{campaign_id}/pledge", json={"user_name": "leo", "amount": 300})
    assert pledge.status_code == 201

    db = TestingSessionLocal()
    try:
        db.execute(
            text("UPDATE campaigns SET deadline = :deadline WHERE id = :id"),
            {"deadline": (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None), "id": campaign_id},
        )
        db.commit()
    finally:
        db.close()

    refund = client.post(f"/campaigns/{campaign_id}/refunds")
    assert refund.status_code == 400

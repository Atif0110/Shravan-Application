import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "Backend"
sys.path.insert(0, str(BACKEND))

from app import app, db
from models import Roles


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-012345678901234567890123456789",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SESSION_PERMANENT=False,
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add_all([
            Roles(name="user", description="General User"),
            Roles(name="caretaker", description="Caretaker"),
            Roles(name="ngo", description="NGO"),
        ])
        db.session.commit()
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def csrf(client):
    response = client.get("/api/csrf-token")
    assert response.status_code == 200
    return response.get_json()["csrf_token"]

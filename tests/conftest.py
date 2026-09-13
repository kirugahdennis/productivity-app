import pytest

from server.app import create_app
from server.extensions import db as _db
from server.config import Config


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "test-secret"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def signup(client, username="alice", password="password123"):
    return client.post("/signup", json={"username": username, "password": password})


def login(client, username="alice", password="password123"):
    return client.post("/login", json={"username": username, "password": password})
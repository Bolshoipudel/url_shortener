import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_shorten_and_redirect(client):
    """POST /shorten создаёт короткую ссылку, GET /{short_id} редиректит"""
    resp = client.post("/shorten", json={"url": "https://example.com/very/long/path"})
    assert resp.status_code == 200
    data = resp.json()
    assert "short_id" in data
    assert "short_url" in data

    short_id = data["short_id"]
    redirect_resp = client.get(f"/{short_id}", follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"] == "https://example.com/very/long/path"


def test_stats_counts_clicks(client):
    """GET /stats/{short_id} возвращает число переходов, счётчик увеличивается"""
    resp = client.post("/shorten", json={"url": "https://example.com"})
    short_id = resp.json()["short_id"]

    stats = client.get(f"/stats/{short_id}").json()
    assert stats["clicks"] == 0

    client.get(f"/{short_id}", follow_redirects=False)
    client.get(f"/{short_id}", follow_redirects=False)

    stats = client.get(f"/stats/{short_id}").json()
    assert stats["clicks"] == 2


def test_not_found(client):
    assert client.get("/nonexistent").status_code == 404
    assert client.get("/stats/nonexistent").status_code == 404

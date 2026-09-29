"""Admins correcting and undoing matches (AN-API is faked).

    uv run --no-project --with flask --with flask_pymongo --with 'pymongo<4.9' --with mongomock \\
        --with requests --with markdown --with pillow --with pytest pytest tests
"""

import sys
from pathlib import Path

import mongomock
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import an_api  # noqa: E402
import flask_app  # noqa: E402
from extensions import mongo  # noqa: E402
from matches import routes  # noqa: E402

TEAM_MATCH = {
    "mode": "Escort", "map": "Rome", "date": "2026-09-01", "outcome": 1, "host": "Alice", "new": False,
    "team1": [{"player": "Alice", "score": 900, "kills": 5, "deaths": 1, "mmrchange": 12.0}],
    "team2": [{"player": "Bob", "score": 400, "kills": 1, "deaths": 5, "mmrchange": -12.0}],
}


@pytest.fixture
def app(monkeypatch):
    app = flask_app.create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")
    cx = mongomock.MongoClient()
    monkeypatch.setattr(mongo, "cx", cx, raising=False)
    monkeypatch.setattr(mongo, "db", cx["public"], raising=False)
    db = cx["public"]
    db.players.insert_many([
        {"name": "Admin", "privilege": 1, "api_key": "tok-admin", "hidden": False},
        {"name": "Alice", "privilege": 10, "hidden": False},
        {"name": "Bob", "privilege": 10, "hidden": False},
        {"name": "NoKey", "privilege": 5, "hidden": False},
    ])
    app.match_id = str(db.matches.insert_one(dict(TEAM_MATCH)).inserted_id)
    calls = []
    app.api_calls = calls

    def fake_post(path, payload=None, token=None, params=None, timeout=None):
        calls.append((path, payload, token))
        return app.api_answer

    app.api_answer = (200, {"status": "done", "result": {"replayed": 2}})
    monkeypatch.setattr(an_api, "post", fake_post)
    return app


def login(client, name):
    with client.session_transaction() as s:
        s["player"] = name
        s["csrf_token"] = "tok"


def test_only_admins_see_and_use_the_controls(app):
    client = app.test_client()
    page = client.get(f"/match/{app.match_id}").get_data(as_text=True)
    assert "/correct" not in page
    login(client, "Alice")
    assert "/correct" not in client.get(f"/match/{app.match_id}").get_data(as_text=True)
    assert client.get(f"/match/{app.match_id}/correct").status_code == 302  # errors send visitors home
    assert client.post(f"/match/{app.match_id}/undo", data={"csrf_token": "tok"}).status_code == 302
    assert app.api_calls == []

    login(client, "Admin")
    page = client.get(f"/match/{app.match_id}").get_data(as_text=True)
    assert f"/match/{app.match_id}/correct" in page and f"/match/{app.match_id}/undo" in page
    assert "&#9998;" in client.get("/matches").get_data(as_text=True)


def test_correction_sends_only_what_changed(app):
    client = app.test_client()
    login(client, "Admin")
    form = client.get(f"/match/{app.match_id}/correct").get_data(as_text=True)
    assert 'name="team1-0-score" value="900"' in form
    data = {"csrf_token": "tok", "outcome": "1", "map": "Rome", "host": "Alice",
            "team1-0-player": "Alice", "team1-0-score": "950", "team1-0-kills": "5", "team1-0-deaths": "1",
            "team2-0-player": "Bob", "team2-0-score": "400", "team2-0-kills": "1", "team2-0-deaths": "5"}
    resp = client.post(f"/match/{app.match_id}/correct", data=data)
    assert resp.status_code == 302 and resp.headers["Location"].endswith(f"/match/{app.match_id}")
    (path, payload, token), = app.api_calls
    assert path == f"matches/{app.match_id}/edit" and token == "tok-admin"
    assert payload == {"team1": [{"player": "Alice", "score": 950, "kills": 5, "deaths": 1}]}


def test_bad_input_and_api_refusals_keep_the_form(app):
    client = app.test_client()
    login(client, "Admin")
    base = {"csrf_token": "tok", "outcome": "1", "map": "Rome", "host": "Alice",
            "team1-0-player": "Alice", "team1-0-score": "lots", "team1-0-kills": "5", "team1-0-deaths": "1",
            "team2-0-player": "Bob", "team2-0-score": "400", "team2-0-kills": "1", "team2-0-deaths": "5"}
    page = client.post(f"/match/{app.match_id}/correct", data=base)
    assert page.status_code == 200 and "must be a whole number" in page.get_data(as_text=True)
    assert app.api_calls == []

    app.api_answer = (400, {"status": "failed", "error": "outcome 2 contradicts the scores 950 - 400"})
    page = client.post(f"/match/{app.match_id}/correct", data=dict(base, **{"team1-0-score": "950", "outcome": "2"}))
    assert page.status_code == 200 and "contradicts the scores" in page.get_data(as_text=True)


def test_csrf_is_checked(app):
    client = app.test_client()
    login(client, "Admin")
    assert client.post(f"/match/{app.match_id}/undo", data={"csrf_token": "wrong"}).status_code == 302
    assert app.api_calls == []


def test_undo_and_slow_recalculation(app):
    client = app.test_client()
    login(client, "Admin")
    app.api_answer = (202, {"status": "running", "operation": "x"})
    resp = client.post(f"/match/{app.match_id}/undo", data={"csrf_token": "tok"}, follow_redirects=True)
    assert "being recalculated" in resp.get_data(as_text=True)
    assert app.api_calls[0][0] == f"matches/{app.match_id}/undo"


def test_admin_without_api_key_gets_one(app):
    client = app.test_client()
    login(client, "NoKey")
    client.post(f"/match/{app.match_id}/undo", data={"csrf_token": "tok"})
    token = app.api_calls[0][2]
    assert token and mongo.db.players.find_one({"name": "NoKey"})["api_key"] == token

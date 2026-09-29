"""Artifact assault per game: ACR/AC3/AC4 have their own leaderboards and profile panels."""

import sys
from pathlib import Path

import mongomock
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import flask_app  # noqa: E402
import modes  # noqa: E402
from accounts.validation import new_player_doc  # noqa: E402
from extensions import mongo  # noqa: E402
from maps import stats as map_stats  # noqa: E402

BASE_KEYS = ("mh", "e", "do", "dm", "asb", "acraar", "acraad")


def player(name, **fields):
    doc = new_player_doc(name, [name], None)
    for key in list(doc):
        if key.startswith(("ac3", "ac4")):
            del doc[key]  # a player from before the new games existed
    doc.update(fields)
    return doc


@pytest.fixture
def app():
    app = flask_app.create_app()  # before patching: init_app sets up the real client
    app.config.update(TESTING=True, SECRET_KEY="test")
    return app


@pytest.fixture
def db(app, monkeypatch):
    cx = mongomock.MongoClient()
    monkeypatch.setattr(mongo, "cx", cx, raising=False)
    monkeypatch.setattr(mongo, "db", cx["public"], raising=False)
    return cx["public"]


@pytest.fixture
def client(app, db):
    return app.test_client()


def test_registry():
    assert modes.RANKING_MODES["acr/running"] == ("acraar", "ACR AA Running")
    assert "running" not in modes.RANKING_MODES
    assert modes.RANKING_MODES["ac4/defending"] == ("ac4aad", "AC4 AA Defending")
    assert set(BASE_KEYS) < set(modes.MODES) and "ac3aar" in modes.MODES
    assert not {"aar", "aad"} & set(modes.MODES)
    assert modes.is_aa_mode("ACR Artifact assault") and modes.is_aa_mode("AC3 Artifact assault")
    assert not modes.is_aa_mode("Escort")
    assert "ac3aarmmr" in new_player_doc("X", ["X"], None)


def test_map_stats_keep_games_apart(db):
    db.matches.insert_many([
        {"mode": "ACR Artifact assault", "map": "Rome"},
        {"mode": "AC3 Artifact assault", "map": "Rome"},
    ])
    assert map_stats.match_modes({"Rome"}, "acraa") == ["ACR Artifact assault"]
    assert map_stats.match_modes({"Rome"}, "ac3aa") == ["AC3 Artifact assault"]


def test_variant_leaderboard(client, db):
    db.players.insert_many([
        player("Runner", ac3aarmmr=950, ac3aargames={"total": 12, "won": 8, "lost": 4},
               ac3aarstats={"totalscore": 0, "kills": 3, "deaths": 6, "scored": 9, "conceded": 0},
               ac3aarrank=1, ac3aarrankchange=2),
        player("AcrOnly", acraargames={"total": 12, "won": 6, "lost": 6}, acraarrank=1),
    ])
    page = client.get("/ac3/running").get_data(as_text=True)
    assert "Runner" in page and "AcrOnly" not in page and "950" in page
    page = client.get("/acr/running").get_data(as_text=True)
    assert "AcrOnly" in page and "Runner" not in page
    # ACR's old addresses
    assert client.get("/running").headers["Location"].endswith("/acr/running")
    assert client.get("/defending").status_code == 301
    assert client.get("/ac3/defending").status_code == 200


def test_aggregate_boards_with_players_missing_new_modes(client, db):
    db.players.insert_one(player("Old", egames={"total": 11, "won": 6, "lost": 5}))
    for path in ("/allmodes", "/average"):
        page = client.get(path).get_data(as_text=True)
        assert "Old" in page and "AC3 AA Running" in page


def test_profile_shows_each_games_aa(client, db):
    db.players.insert_one(player("Old", ign=["Old"]))
    db.matches.insert_one({
        "mode": "AC4 Artifact assault", "map": "Havana", "date": "2026-09-01", "outcome": 1,
        "team1": [{"player": "Old", "score": 900, "kills": 1, "deaths": 2, "scored": 3, "mmrchange": 5.0}],
        "team2": [{"player": "Other", "score": 800, "kills": 2, "deaths": 1, "scored": 0, "mmrchange": -5.0}],
    })
    page = client.get("/profile/Old").get_data(as_text=True)
    for board in modes.AA_BOARDS:
        assert f'data-mode="{board["name"]}"' in page
        assert f'id="{board["key"]}hist"' in page
    assert 'data-modes="AC4 AA Running,AC4 AA Defending"' in page


def test_match_pages_show_artifacts_for_every_aa_game(client, db):
    mid = db.matches.insert_one({
        "mode": "AC3 Artifact assault", "map": "Rome", "date": "2026-09-01", "outcome": 1,
        "team1": [{"player": "A", "score": 1234, "kills": 1, "deaths": 2, "scored": 7}],
        "team2": [{"player": "B", "score": 999, "kills": 2, "deaths": 1, "scored": 0}],
    }).inserted_id
    detail = client.get(f"/match/{mid}").get_data(as_text=True)
    assert ">7<" in detail and "1234" not in detail


def test_pages_cope_with_missing_counters(client, db):
    # got Assassinate before podiums/finishes were tracked
    db.players.insert_one(player("Legacy", ign=["Legacy"], asbgames={"total": 12, "won": 5, "lost": 7},
                                 asbrank=1, dmgames={"total": 0, "won": 0, "lost": 0}))
    assert client.get("/profile/Legacy").status_code == 200
    assert "Legacy" in client.get("/assassinate").get_data(as_text=True)
    assert client.get("/allmodes").status_code == 200

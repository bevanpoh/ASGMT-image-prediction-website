from flask import json, jsonify

import pytest


def test_login_get(client, capsys):
    with capsys.disabled():
        response = client.get("/login")
        assert response.status_code == 200


@pytest.mark.parametrize(
    "data,expected",
    [
        ({"username": "bevanpoh", "password": "bevandevops"}, 302),
        ({"username": "bevanpoh", "password": "wrongpass"}, 403),
        ({"username": "wronguser", "password": "bevandevops"}, 403),
    ],
)
def test_login_post(data, expected, client, capsys):
    with capsys.disabled():
        response = client.post(
            "/login",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == expected


def test_no_login(client, capsys):
    with capsys.disabled():
        index_response = client.get("/index")
        history_response = client.get("/history")
        delete_response = client.get("/delete/39393939")

        assert index_response.status_code == 307
        assert history_response.status_code == 307
        assert delete_response.status_code == 307


def test_yes_login(client, capsys):
    with capsys.disabled():
        with client.session_transaction() as session:
            session["username"] = "bevanpoh"

        index_response = client.get("/index")
        history_response = client.get("/history")
        delete_response = client.get("/delete/abc")

        assert index_response.status_code == 200
        assert history_response.status_code == 200
        assert delete_response.status_code == 302

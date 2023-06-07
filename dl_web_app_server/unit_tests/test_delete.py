import pytest

from flask import json

# test success failure

def test_delete_success(client, capsys):
    with capsys.disabled():
        with client.session_transaction() as session:
            session["username"] = "bevanpoh"

        response1 = client.post("/add_dummy")
        json_response = json.loads(response1.get_data())
        response2 = client.get(f"/delete/{json_response['id']}")

        assert response2.status_code == 302


def test_delete_fail(client, capsys):
    with capsys.disabled():
        with client.session_transaction() as session:
            session["username"] = "bevanpoh"

        response2 = client.get(f"/delete/")

        assert response2.status_code == 404

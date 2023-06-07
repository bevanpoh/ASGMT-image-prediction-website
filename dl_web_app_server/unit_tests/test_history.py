import pytest

from flask import json


# test arguments
## no args
## col and no method
## method and no col
## bad args


@pytest.mark.parametrize(
    "col,method,page,expected",
    [
        (None, None, -10, 404),
        ("Date Created", None, 1, 404),
        (None, "desc", 1, 404),
        (None, None, None, 200),
        (None, None, 1, 200),
        (None, None, 2, 200),
        ("Date Created", "desc", 1, 200),
    ],
)
def test_get_history(col, method, page, expected, client, capsys):
    with capsys.disabled():
        with client.session_transaction() as session:
            session["username"] = "bevanpoh"

        response = client.get(
            "/history", query_string={"by": col, "method": method, "page": page}
        )

        assert response.status_code == expected

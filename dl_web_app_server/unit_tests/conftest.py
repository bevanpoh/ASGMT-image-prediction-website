import pytest
from app import app as flask_app


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    app.config["WTF_CSRF_ENABLED"] = False
    print(app.static_url_path)
    return app.test_client()

import pytest
from app import create_app
import random


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# Checks the id of number one result craftsman
def test_json_data(client):
    response = client.get("/craftsmen?postalcode=85375")
    assert response.json["craftsmen"][0]["id"] == 10642
    
def test_update(client):
    numba = random.randrange(1, 100000)
    response = client.patch("/craftman/1", json={"maxDrivingDistance": numba})
    assert response.json["updated"]["maxDrivingDistance"]
from http import HTTPStatus

from fastapi.testclient import TestClient

from infrastructure.fastapi.main import create_api

client = TestClient(create_api())


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == HTTPStatus.OK


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == HTTPStatus.OK

from http import HTTPStatus

from fastapi.testclient import TestClient


def test_healthz(client: TestClient):
    response = client.get("/healthz/live")
    assert response.status_code == HTTPStatus.OK


def test_readyz(client: TestClient):
    response = client.get("/healthz/ready")
    assert response.status_code == HTTPStatus.OK

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_http_errors_use_standard_envelope() -> None:
    client = TestClient(create_app())

    response = client.get("/missing")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "http_error", "message": "Not Found"}
    }


def test_validation_errors_use_standard_envelope() -> None:
    application = create_app()

    @application.get("/test-validation")
    async def validation_endpoint(value: int) -> dict[str, int]:
        return {"value": value}

    response = TestClient(application).get("/test-validation", params={"value": "invalid"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["details"][0]["location"] == ["query", "value"]


def test_unexpected_errors_do_not_expose_internal_details() -> None:
    application = create_app()

    @application.get("/test-error")
    async def error_endpoint() -> None:
        raise RuntimeError("internal detail")

    response = TestClient(application, raise_server_exceptions=False).get("/test-error")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred",
        }
    }


def test_openapi_documentation_is_available() -> None:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]
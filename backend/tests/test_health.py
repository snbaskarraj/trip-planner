def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_runtime_reports_database_dialect(client):
    response = client.get("/api/runtime")
    assert response.status_code == 200
    assert "database" in response.json()
    assert response.json()["database"] in {"sqlite", "postgresql"}

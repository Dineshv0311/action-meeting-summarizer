from run import create_app


def test_health_check():
    client = create_app().test_client()
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

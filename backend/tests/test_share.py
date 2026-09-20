def test_share_link_is_readable_without_login(client, trip):
    token = trip["share_token"]
    response = client.get(f"/api/share/{token}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == trip["id"]
    assert body["title"] == trip["title"]
    assert body["share_token"] == token


def test_share_routes_do_not_accept_writes(client, trip):
    token = trip["share_token"]
    assert client.post(f"/api/share/{token}", json={"title": "hacked"}).status_code == 405
    assert client.patch(f"/api/share/{token}", json={"title": "hacked"}).status_code == 405
    assert client.delete(f"/api/share/{token}").status_code == 405

    still = client.get(f"/api/share/{token}")
    assert still.status_code == 200
    assert still.json()["title"] == trip["title"]


def test_unknown_share_token_is_404(client):
    response = client.get("/api/share/not-a-real-token")
    assert response.status_code == 404

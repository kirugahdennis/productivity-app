from tests.conftest import signup, login


class TestAuth:
    def test_signup_creates_user_and_logs_in(self, client):
        resp = signup(client)
        assert resp.status_code == 201
        assert resp.json["username"] == "alice"
        assert "password" not in resp.json
        assert "_password_hash" not in resp.json

        # signup should also establish a session
        check = client.get("/check_session")
        assert check.status_code == 200

    def test_signup_rejects_duplicate_username(self, client):
        signup(client)
        resp = signup(client)
        assert resp.status_code == 422

    def test_signup_rejects_short_password(self, client):
        resp = client.post("/signup", json={"username": "bob", "password": "123"})
        assert resp.status_code == 422

    def test_login_with_correct_credentials(self, client):
        signup(client)
        client.delete("/logout")
        resp = login(client)
        assert resp.status_code == 200
        assert resp.json["username"] == "alice"

    def test_login_with_wrong_password_fails(self, client):
        signup(client)
        resp = login(client, password="wrongpassword")
        assert resp.status_code == 401

    def test_login_with_nonexistent_user_fails(self, client):
        resp = login(client, username="ghost")
        assert resp.status_code == 401

    def test_check_session_without_login(self, client):
        resp = client.get("/check_session")
        assert resp.status_code == 401

    def test_logout_clears_session(self, client):
        signup(client)
        resp = client.delete("/logout")
        assert resp.status_code == 204

        check = client.get("/check_session")
        assert check.status_code == 401

    def test_logout_requires_login(self, client):
        resp = client.delete("/logout")
        assert resp.status_code == 401
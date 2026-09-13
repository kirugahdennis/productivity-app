from tests.conftest import signup, login


def create_entry(client, title="My Day", content="It was fine.", mood="calm"):
    return client.post(
        "/journal_entries", json={"title": title, "content": content, "mood": mood}
    )


class TestJournalEntryAccess:
    def test_index_requires_login(self, client):
        resp = client.get("/journal_entries")
        assert resp.status_code == 401

    def test_create_requires_login(self, client):
        resp = create_entry(client)
        assert resp.status_code == 401


class TestJournalEntryCRUD:
    def test_create_and_list_entry(self, client):
        signup(client)
        resp = create_entry(client)
        assert resp.status_code == 201
        assert resp.json["title"] == "My Day"
        assert resp.json["mood"] == "calm"

        listing = client.get("/journal_entries")
        assert listing.status_code == 200
        assert listing.json["meta"]["total_items"] == 1
        assert len(listing.json["entries"]) == 1

    def test_create_rejects_empty_title(self, client):
        signup(client)
        resp = create_entry(client, title="")
        assert resp.status_code == 422

    def test_create_rejects_invalid_mood(self, client):
        signup(client)
        resp = create_entry(client, mood="furious")
        assert resp.status_code == 422

    def test_get_single_entry(self, client):
        signup(client)
        created = create_entry(client)
        entry_id = created.json["id"]

        resp = client.get(f"/journal_entries/{entry_id}")
        assert resp.status_code == 200
        assert resp.json["id"] == entry_id

    def test_get_nonexistent_entry_returns_404(self, client):
        signup(client)
        resp = client.get("/journal_entries/9999")
        assert resp.status_code == 404

    def test_patch_updates_entry(self, client):
        signup(client)
        created = create_entry(client)
        entry_id = created.json["id"]

        resp = client.patch(f"/journal_entries/{entry_id}", json={"title": "New Title"})
        assert resp.status_code == 200
        assert resp.json["title"] == "New Title"
        assert resp.json["content"] == "It was fine."

    def test_patch_rejects_invalid_data(self, client):
        signup(client)
        created = create_entry(client)
        entry_id = created.json["id"]

        resp = client.patch(f"/journal_entries/{entry_id}", json={"title": ""})
        assert resp.status_code == 422

    def test_delete_removes_entry(self, client):
        signup(client)
        created = create_entry(client)
        entry_id = created.json["id"]

        resp = client.delete(f"/journal_entries/{entry_id}")
        assert resp.status_code == 204

        follow_up = client.get(f"/journal_entries/{entry_id}")
        assert follow_up.status_code == 404


class TestJournalEntryOwnership:
    def test_user_cannot_view_another_users_entry(self, client):
        signup(client, username="alice")
        created = create_entry(client)
        entry_id = created.json["id"]
        client.delete("/logout")

        signup(client, username="bob")
        resp = client.get(f"/journal_entries/{entry_id}")
        assert resp.status_code == 404

    def test_user_cannot_update_another_users_entry(self, client):
        signup(client, username="alice")
        created = create_entry(client)
        entry_id = created.json["id"]
        client.delete("/logout")

        signup(client, username="bob")
        resp = client.patch(f"/journal_entries/{entry_id}", json={"title": "Hacked"})
        assert resp.status_code == 404

    def test_user_cannot_delete_another_users_entry(self, client):
        signup(client, username="alice")
        created = create_entry(client)
        entry_id = created.json["id"]
        client.delete("/logout")

        signup(client, username="bob")
        resp = client.delete(f"/journal_entries/{entry_id}")
        assert resp.status_code == 404

        # confirm alice's entry is untouched
        client.delete("/logout")
        login(client, username="alice")
        still_there = client.get(f"/journal_entries/{entry_id}")
        assert still_there.status_code == 200

    def test_index_only_returns_own_entries(self, client):
        signup(client, username="alice")
        create_entry(client, title="Alice Entry")
        client.delete("/logout")

        signup(client, username="bob")
        create_entry(client, title="Bob Entry 1")
        create_entry(client, title="Bob Entry 2")

        resp = client.get("/journal_entries")
        titles = [e["title"] for e in resp.json["entries"]]
        assert titles == ["Bob Entry 2", "Bob Entry 1"]
        assert resp.json["meta"]["total_items"] == 2


class TestPagination:
    def test_pagination_pages_correctly(self, client):
        signup(client)
        for i in range(25):
            create_entry(client, title=f"Entry {i}")

        page1 = client.get("/journal_entries?page=1&per_page=10")
        assert page1.status_code == 200
        assert len(page1.json["entries"]) == 10
        assert page1.json["meta"]["total_pages"] == 3
        assert page1.json["meta"]["has_next"] is True
        assert page1.json["meta"]["has_prev"] is False

        page3 = client.get("/journal_entries?page=3&per_page=10")
        assert len(page3.json["entries"]) == 5
        assert page3.json["meta"]["has_next"] is False
        assert page3.json["meta"]["has_prev"] is True

    def test_per_page_is_capped(self, client):
        signup(client)
        for i in range(5):
            create_entry(client, title=f"Entry {i}")

        resp = client.get("/journal_entries?per_page=999")
        assert resp.json["meta"]["per_page"] == 50

    def test_defaults_used_for_invalid_params(self, client):
        signup(client)
        create_entry(client)

        resp = client.get("/journal_entries?page=abc&per_page=xyz")
        assert resp.status_code == 200
        assert resp.json["meta"]["page"] == 1
        assert resp.json["meta"]["per_page"] == 10
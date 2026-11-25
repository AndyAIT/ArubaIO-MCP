import pytest

import aruba_client
from aruba_client import ArubaInstantOnClient

SITES = [
    {"id": "11111111-aaaa", "name": "Contoso IT"},
    {"id": "22222222-bbbb", "name": "Fabrikam Health Plus"},
    {"id": "33333333-cccc", "name": "Fabrikam Dental"},
]


@pytest.fixture
def client():
    c = ArubaInstantOnClient()
    c.list_sites = lambda: SITES
    return c


def test_resolve_by_uuid_name_and_prefix(client):
    assert client.resolve_site_id("22222222-bbbb") == "22222222-bbbb"
    assert client.resolve_site_id("contoso it") == "11111111-aaaa"
    assert client.resolve_site_id("Contoso") == "11111111-aaaa"


def test_resolve_ambiguous_prefix_raises(client):
    with pytest.raises(ValueError, match="Multiple sites"):
        client.resolve_site_id("Fabrikam")


def test_resolve_unknown_raises(client):
    with pytest.raises(ValueError, match="No site found"):
        client.resolve_site_id("nope")


def test_list_clients_filters_by_type(client):
    client._get = lambda path: {
        "elements": [
            {"id": 1, "clientType": "wired"},
            {"id": 2, "clientType": "wireless"},
            {"id": 3, "clientType": "wireless"},
        ]
    }
    assert [c["id"] for c in client.list_clients("Contoso IT", "wireless")] == [2, 3]
    assert [c["id"] for c in client.list_clients("Contoso IT", "wired")] == [1]
    assert len(client.list_clients("Contoso IT")) == 3


def test_get_site_resource_returns_elements_for_lists(client):
    client._get = lambda path: {"elements": [1, 2], "kind": "x"}
    assert client.get_site_resource("Contoso IT", "alerts", list_result=True) == [1, 2]
    assert client.get_site_resource("Contoso IT", "summary")["kind"] == "x"


def test_get_reauthenticates_once_on_401(monkeypatch):
    c = ArubaInstantOnClient()
    auth_calls = []

    def fake_auth():
        auth_calls.append(1)
        c.access_token = "tok"
        c.token_expires_at = float("inf")

    c.authenticate = fake_auth

    class Resp:
        def __init__(self, status):
            self.status_code = status

        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    statuses = iter([401, 200])
    c.session.get = lambda *a, **k: Resp(next(statuses))
    assert c._get("/api/x") == {"ok": True}
    assert len(auth_calls) == 2


def test_site_cache_is_reused(monkeypatch):
    c = ArubaInstantOnClient()
    calls = []
    c._get = lambda path: calls.append(path) or {"elements": SITES}
    c.resolve_site_id("Contoso IT")
    c.resolve_site_id("Contoso IT")
    assert len(calls) == 1

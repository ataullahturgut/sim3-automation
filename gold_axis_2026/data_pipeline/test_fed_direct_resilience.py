from __future__ import annotations

import pytest

import fed_direct


class FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        return self.responses.pop(0)


def test_get_retries_empty_http_body_then_succeeds(monkeypatch):
    monkeypatch.setattr(fed_direct.time_mod, "sleep", lambda _: None)
    session = FakeSession([
        FakeResponse(b""),
        FakeResponse(b"   \n"),
        FakeResponse(b"usable"),
    ])
    response = fed_direct._get(session, "https://example.invalid")
    assert response.content == b"usable"
    assert session.calls == 3


def test_get_fails_closed_after_repeated_empty_http_body(monkeypatch):
    monkeypatch.setattr(fed_direct.time_mod, "sleep", lambda _: None)
    session = FakeSession([FakeResponse(b""), FakeResponse(b""), FakeResponse(b"")])
    with pytest.raises(RuntimeError, match="FED_DIRECT_EMPTY_HTTP_BODY"):
        fed_direct._get(session, "https://example.invalid")
    assert session.calls == 3


def test_read_frb_package_names_empty_body():
    with pytest.raises(ValueError, match="FRB_DDP_EMPTY_BODY"):
        fed_direct._read_frb_package(b"")


def test_read_frb_package_names_empty_csv_after_metadata_rows():
    payload = b"m1\nm2\nm3\nm4\nm5\n"
    with pytest.raises(ValueError, match="FRB_DDP_EMPTY_CSV"):
        fed_direct._read_frb_package(payload)

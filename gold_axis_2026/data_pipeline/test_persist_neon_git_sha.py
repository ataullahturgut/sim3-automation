from __future__ import annotations

from types import SimpleNamespace

import persist_neon


CANONICAL = "1" * 40
CALLER = "2" * 40
OVERRIDE = "3" * 40


def test_code_git_sha_prefers_explicit_override(monkeypatch):
    monkeypatch.setenv("GOLD_CODE_SHA", OVERRIDE)
    monkeypatch.setenv("GITHUB_SHA", CALLER)
    monkeypatch.setattr(
        persist_neon.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=CANONICAL + "\n"),
    )
    assert persist_neon._code_git_sha() == OVERRIDE


def test_code_git_sha_prefers_checked_out_head_over_caller(monkeypatch):
    monkeypatch.delenv("GOLD_CODE_SHA", raising=False)
    monkeypatch.setenv("GITHUB_SHA", CALLER)
    monkeypatch.setattr(
        persist_neon.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout=CANONICAL + "\n"),
    )
    assert persist_neon._code_git_sha() == CANONICAL


def test_code_git_sha_falls_back_to_github_sha_when_git_unavailable(monkeypatch):
    monkeypatch.delenv("GOLD_CODE_SHA", raising=False)
    monkeypatch.setenv("GITHUB_SHA", CALLER)

    def unavailable(*args, **kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(persist_neon.subprocess, "run", unavailable)
    assert persist_neon._code_git_sha() == CALLER


def test_code_git_sha_rejects_invalid_explicit_override(monkeypatch):
    monkeypatch.setenv("GOLD_CODE_SHA", "not-a-sha")
    try:
        persist_neon._code_git_sha()
    except RuntimeError as exc:
        assert str(exc) == "INVALID_GOLD_CODE_SHA"
    else:
        raise AssertionError("invalid override must fail closed")

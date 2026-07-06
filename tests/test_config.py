"""Tests for configuration helpers."""

from config import session_cookie_secure


def test_session_cookie_secure_defaults_false(monkeypatch):
    monkeypatch.delenv('PROXYWAKE_SESSION_COOKIE_SECURE', raising=False)
    assert session_cookie_secure() is False


def test_session_cookie_secure_truthy_values(monkeypatch):
    for value in ('1', 'true', 'TRUE', 'yes', 'on'):
        monkeypatch.setenv('PROXYWAKE_SESSION_COOKIE_SECURE', value)
        assert session_cookie_secure() is True


def test_session_cookie_secure_false_values(monkeypatch):
    for value in ('0', 'false', 'no', 'off'):
        monkeypatch.setenv('PROXYWAKE_SESSION_COOKIE_SECURE', value)
        assert session_cookie_secure() is False

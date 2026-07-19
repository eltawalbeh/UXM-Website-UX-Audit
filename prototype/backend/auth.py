from __future__ import annotations

import hmac
import os
import secrets
import threading
import time
from http.cookies import CookieError, SimpleCookie


SESSION_COOKIE_NAME = "uxm_operator_session"
SESSION_TTL_SECONDS = 8 * 60 * 60


def configured_operator() -> tuple[str, str] | None:
    email = os.getenv("UXM_OPERATOR_EMAIL", "").strip().lower()
    password = os.getenv("UXM_OPERATOR_PASSWORD", "")
    return (email, password) if email and password else None


def verify_credentials(email: str, password: str) -> bool:
    """Validate both supplied fields without short-circuiting either comparison."""
    operator = configured_operator()
    expected_email, expected_password = operator if operator is not None else ("", "")
    email_matches = hmac.compare_digest(email.strip().lower(), expected_email)
    password_matches = hmac.compare_digest(password, expected_password)
    return operator is not None and email_matches and password_matches


class SessionStore:
    def __init__(self, ttl_seconds: int = SESSION_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, float] = {}
        self._lock = threading.Lock()

    def issue(self) -> str:
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._sessions[token] = time.monotonic() + self.ttl_seconds
        return token

    def active(self, token: str | None) -> bool:
        if not token:
            return False
        with self._lock:
            expires_at = self._sessions.get(token)
            if expires_at is None or expires_at <= time.monotonic():
                self._sessions.pop(token, None)
                return False
            return True

    def revoke(self, token: str | None) -> None:
        if token:
            with self._lock:
                self._sessions.pop(token, None)


def session_token(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    try:
        cookie.load(cookie_header)
    except (CookieError, KeyError):
        return None
    morsel = cookie.get(SESSION_COOKIE_NAME)
    return morsel.value if morsel else None


def session_cookie(token: str, max_age: int = SESSION_TTL_SECONDS, secure: bool = True) -> str:
    cookie = SimpleCookie()
    cookie[SESSION_COOKIE_NAME] = token
    cookie[SESSION_COOKIE_NAME]["path"] = "/"
    cookie[SESSION_COOKIE_NAME]["max-age"] = str(max_age)
    cookie[SESSION_COOKIE_NAME]["httponly"] = True
    if secure:
        cookie[SESSION_COOKIE_NAME]["secure"] = True
    cookie[SESSION_COOKIE_NAME]["samesite"] = "Strict"
    return cookie.output(header="").strip()

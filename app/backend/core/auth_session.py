from __future__ import annotations

from typing import Any


SESSION_USER_KEY = "auth_app_user"


def build_session_user(record: dict[str, Any] | None) -> dict[str, Any] | None:
    if not record:
        return None

    return {
        "id": record.get("id"),
        "username": record.get("username"),
        "email": record.get("email"),
        "first_name": record.get("first_name"),
        "last_name": record.get("last_name"),
        "is_active": record.get("is_active"),
        "is_superuser": record.get("is_superuser"),
    }


def login_app_user(request, record: dict[str, Any]) -> dict[str, Any]:
    session_user = build_session_user(record) or {}
    request.session.cycle_key()
    request.session[SESSION_USER_KEY] = session_user
    request.app_user = session_user
    return session_user


def logout_app_user(request) -> None:
    request.session.pop(SESSION_USER_KEY, None)
    request.app_user = None


def get_session_user(request) -> dict[str, Any] | None:
    return request.session.get(SESSION_USER_KEY)


def is_authenticated(request) -> bool:
    session_user = get_session_user(request)
    return bool(session_user and session_user.get("id"))

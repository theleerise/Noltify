from backend.core.auth_session import get_session_user


def auth_app_context(request):
    session_user = get_session_user(request)
    return {
        "app_session_user": session_user,
        "app_is_authenticated": bool(session_user and session_user.get("id")),
    }

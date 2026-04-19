from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse

from backend.core.auth_session import get_session_user
from backend.core.response import get_error_response
from backend.managers.authorization_manager import AuthorizationManager


ADMIN_GENERAL_ROLE_CODE = "ADMIN_GENERAL"
JSON_URL_NAMES = {
    "data",
    "new",
    "edit",
    "create",
    "update",
    "delete",
    "general_data",
    "general_create",
    "general_update",
    "general_delete",
}
HTML_REDIRECT_URL_NAMES = {
    "list",
    "general",
    "profile",
}


def _normalize_codes(*codes: str | None) -> tuple[str, ...]:
    return tuple(
        str(code).strip().upper()
        for code in codes
        if code and str(code).strip()
    )


def _get_current_user_id(request) -> int | None:
    session_user = getattr(request, "app_user", None) or get_session_user(request) or {}
    try:
        return int(session_user.get("id"))
    except (TypeError, ValueError):
        return None


def _is_superuser(request) -> bool:
    session_user = getattr(request, "app_user", None) or get_session_user(request) or {}
    return bool(session_user.get("is_superuser"))


def _wants_json_response(request) -> bool:
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", "") or ""

    if request.method != "GET":
        return True

    if url_name in JSON_URL_NAMES:
        return True

    accept_header = request.headers.get("Accept", "")
    return "application/json" in accept_header.lower()


def _build_unauthorized_response(request, message: str):
    if _wants_json_response(request):
        return get_error_response(message, status=401)

    login_url = reverse("auth_app:login")
    return HttpResponseRedirect(f"{login_url}?next={request.get_full_path()}")


def _build_forbidden_response(request, message: str):
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", "") or ""

    if _wants_json_response(request):
        return get_error_response(message, status=403)

    if url_name in HTML_REDIRECT_URL_NAMES:
        return HttpResponseRedirect(reverse("home"))

    return HttpResponseForbidden(message)


def get_request_access_profile(request) -> dict[str, set[str]]:
    cached_profile = getattr(request, "_app_access_profile", None)
    if cached_profile is not None:
        return cached_profile

    empty_profile = {"role_codes": set(), "permission_codes": set()}
    if _is_superuser(request):
        request._app_access_profile = empty_profile
        return empty_profile

    user_id = _get_current_user_id(request)
    if not user_id:
        request._app_access_profile = empty_profile
        return empty_profile

    manager = AuthorizationManager()
    request._app_access_profile = manager.get_access_profile(user_id)
    return request._app_access_profile


def get_request_role_codes(request) -> set[str]:
    return set(get_request_access_profile(request).get("role_codes", set()))


def get_request_permission_codes(request) -> set[str]:
    return set(get_request_access_profile(request).get("permission_codes", set()))


def user_has_role(request, *role_codes: str) -> bool:
    normalized_codes = _normalize_codes(*role_codes)
    if not normalized_codes:
        return False

    if _is_superuser(request):
        return True

    user_role_codes = get_request_role_codes(request)
    return any(code in user_role_codes for code in normalized_codes)


def user_has_permission(request, *permission_codes: str, require_all: bool = False) -> bool:
    normalized_codes = _normalize_codes(*permission_codes)
    if not normalized_codes:
        return False

    if _is_superuser(request):
        return True

    user_permission_codes = get_request_permission_codes(request)
    if require_all:
        return all(code in user_permission_codes for code in normalized_codes)
    return any(code in user_permission_codes for code in normalized_codes)


def require_app_session(view_func: Callable):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        session_user = getattr(request, "app_user", None) or get_session_user(request)
        if not session_user or not session_user.get("id"):
            return _build_unauthorized_response(
                request,
                "Debes iniciar sesion para acceder a esta seccion",
            )
        return view_func(request, *args, **kwargs)

    return wrapper


def require_superuser(message: str | None = None):
    def decorator(view_func: Callable):
        @wraps(view_func)
        @require_app_session
        def wrapper(request, *args, **kwargs):
            if _is_superuser(request):
                return view_func(request, *args, **kwargs)

            final_message = message or "Solo los superusuarios pueden acceder a este recurso"
            return _build_forbidden_response(request, final_message)

        return wrapper

    return decorator


def require_permission(*permission_codes: str, require_all: bool = False, message: str | None = None):
    normalized_codes = _normalize_codes(*permission_codes)

    def decorator(view_func: Callable):
        @wraps(view_func)
        @require_app_session
        def wrapper(request, *args, **kwargs):
            if not normalized_codes:
                return view_func(request, *args, **kwargs)

            if user_has_permission(request, *normalized_codes, require_all=require_all):
                return view_func(request, *args, **kwargs)

            final_message = message or "No tienes permisos para acceder a este recurso"
            return _build_forbidden_response(request, final_message)

        return wrapper

    return decorator


def require_any_permission(*permission_codes: str, message: str | None = None):
    return require_permission(*permission_codes, require_all=False, message=message)


def build_crud_permission_map(permission_prefix: str) -> dict[str, tuple[str, ...]]:
    normalized_prefix = str(permission_prefix).strip().upper()
    list_code = f"{normalized_prefix}_LIST"
    insert_code = f"{normalized_prefix}_INSERT"
    update_code = f"{normalized_prefix}_UPDATE"
    delete_code = f"{normalized_prefix}_DELETE"

    return {
        "list_view": (list_code,),
        "data": (list_code,),
        "form_view": (list_code, insert_code, update_code),
        "new_view": (insert_code,),
        "edit_view": (update_code,),
        "create": (insert_code,),
        "update": (update_code,),
        "delete": (delete_code,),
    }

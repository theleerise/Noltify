from backend.core.auth_session import get_session_user
from backend.core.authorization import (
    ADMIN_GENERAL_ROLE_CODE,
    get_request_permission_codes,
    get_request_role_codes,
    user_has_permission,
    user_has_role,
)


def auth_app_context(request):
    session_user = get_session_user(request)
    permission_codes = get_request_permission_codes(request) if session_user and session_user.get("id") else set()
    role_codes = get_request_role_codes(request) if session_user and session_user.get("id") else set()
    can_view_admin_menu = user_has_role(request, ADMIN_GENERAL_ROLE_CODE) if session_user and session_user.get("id") else False
    can_view_document_admin = user_has_role(request, ADMIN_GENERAL_ROLE_CODE, "DOCUMENT_ADMIN") if session_user and session_user.get("id") else False
    can_view_publication_admin = user_has_role(request, ADMIN_GENERAL_ROLE_CODE, "PUBLICATION_ADMIN") if session_user and session_user.get("id") else False
    return {
        "app_session_user": session_user,
        "app_is_authenticated": bool(session_user and session_user.get("id")),
        "app_permission_codes": permission_codes,
        "app_role_codes": role_codes,
        "app_is_superuser": bool(session_user and session_user.get("is_superuser")),
        "app_can_view_admin_menu": can_view_admin_menu,
        "app_can_view_management_menu": can_view_document_admin or can_view_publication_admin,
        "app_can_view_document_admin": can_view_document_admin,
        "app_can_view_publication_admin": can_view_publication_admin,
        "app_can_manage_documents": user_has_permission(request, "DOCUMENT_LIST") if session_user and session_user.get("id") else False,
        "app_can_manage_publications": user_has_permission(request, "PUBLICATION_LIST") if session_user and session_user.get("id") else False,
    }

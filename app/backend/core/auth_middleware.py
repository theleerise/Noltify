from django.http import HttpResponseRedirect
from django.urls import reverse

from backend.core.auth_session import get_session_user


class AuthAppMiddleware:
    PUBLIC_PREFIXES = (
        "/admin/",
        "/health/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.app_user = get_session_user(request)

        login_url = reverse("auth_app:login")
        logout_url = reverse("auth_app:logout")
        current_path = request.path

        is_public_path = (
            current_path == login_url
            or current_path == logout_url
            or current_path == "/favicon.ico"
            or current_path.startswith(self.PUBLIC_PREFIXES)
        )

        is_authenticated = bool(request.app_user and request.app_user.get("id"))

        if not is_authenticated and not is_public_path:
            redirect_response = HttpResponseRedirect(f"{login_url}?next={request.get_full_path()}")
            return redirect_response

        if is_authenticated and current_path == login_url:
            return HttpResponseRedirect(reverse("home"))

        return self.get_response(request)

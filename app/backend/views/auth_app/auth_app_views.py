"""
Vistas relacionadas con auth app.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from backend.core.auth_session import login_app_user, logout_app_user
from backend.managers.app_user_manager import AppUserManager


def _get_safe_redirect(request, candidate_url: str | None) -> str:
    """
    Recupera la información necesaria para `_get_safe_redirect`.

    La función concentra una lectura o resolucin de datos reutilizable dentro del módulo.

    Args:
        request: Objeto request actual de Django.
        candidate_url: Valor de entrada utilizado por la operación.

    Returns:
        _type_: Valor resuelto a partir de la lógica interna de la función.
    """
    default_url = "/"
    if candidate_url and url_has_allowed_host_and_scheme(
        candidate_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate_url

    return default_url


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Procesa la petición asociada a `login_view`.

    La función valida la entrada necesaria y devuelve la respuesta HTTP correspondiente segn el contexto de negocio.

    Args:
        request: Objeto request actual de Django.

    Returns:
        _type_: Respuesta HTTP o JSON generada para la petición actual.
    """
    next_url = _get_safe_redirect(request, request.GET.get("next") or request.POST.get("next"))
    context_page = {
        "next_url": next_url,
        "login_value": "",
        "error_message": None,
    }

    if request.method == "GET":
        return render(request, "auth_app/login.html", context_page)

    login_value = (request.POST.get("login") or "").strip()
    password = request.POST.get("password") or ""

    context_page["login_value"] = login_value

    if not login_value or not password:
        context_page["error_message"] = "Debes informar usuario o email y la contrasea."
        return render(request, "auth_app/login.html", context_page, status=400)

    manager = AppUserManager()
    user_record = manager.get_by_login(login_value)

    if not user_record or not check_password(password, user_record.get("password_hash") or ""):
        context_page["error_message"] = "Credenciales incorrectas."
        return render(request, "auth_app/login.html", context_page, status=401)

    login_app_user(request, user_record)
    return redirect(next_url)


@require_http_methods(["POST", "GET"])
def logout_view(request):
    """
    Procesa la petición asociada a `logout_view`.

    La función valida la entrada necesaria y devuelve la respuesta HTTP correspondiente segn el contexto de negocio.

    Args:
        request: Objeto request actual de Django.

    Returns:
        _type_: Respuesta HTTP o JSON generada para la petición actual.
    """
    logout_app_user(request)
    request.session.cycle_key()
    return redirect("auth_app:login")

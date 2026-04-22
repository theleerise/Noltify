"""
Utilidades de autorización y control de acceso de la aplicación.

Este módulo centraliza la lógica relacionada con roles, permisos, sesiones
autenticadas y decoradores reutilizables para proteger vistas. También adapta
la respuesta de acceso denegado según si la petición espera HTML o JSON.
"""

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
    """
    Normaliza una colección de códigos de rol o permiso.

    El objetivo de este método es asegurar que todos los códigos comparados se
    encuentren en un formato homogéneo, eliminando espacios sobrantes y
    convirtiendo el contenido a mayúsculas.

    Args:
        *codes (str | None): Códigos recibidos para ser normalizados.

    Returns:
        tuple[str, ...]: Tupla con los códigos válidos, limpios y en mayúsculas.
    """
    return tuple(
        str(code).strip().upper()
        for code in codes
        if code and str(code).strip()
    )


def _get_current_user_id(request) -> int | None:
    """
    Obtiene el identificador del usuario autenticado asociado a la petición.

    El método revisa primero el atributo `app_user` inyectado en la request y,
    si no existe, consulta la sesión. Si el identificador no puede convertirse
    correctamente a entero, devuelve `None`.

    Args:
        request: Objeto request actual de Django.

    Returns:
        int | None: Identificador del usuario autenticado o `None` si no existe.
    """
    session_user = getattr(request, "app_user", None) or get_session_user(request) or {}
    try:
        return int(session_user.get("id"))
    except (TypeError, ValueError):
        return None


def _is_superuser(request) -> bool:
    """
    Indica si el usuario autenticado de la petición es superusuario.

    Args:
        request: Objeto request actual de Django.

    Returns:
        bool: `True` si el usuario tiene privilegios de superusuario,
        `False` en caso contrario.
    """
    session_user = getattr(request, "app_user", None) or get_session_user(request) or {}
    return bool(session_user.get("is_superuser"))


def _wants_json_response(request) -> bool:
    """
    Determina si una respuesta de error debe devolverse en formato JSON.

    Se considera que la petición espera JSON cuando no es una petición GET,
    cuando la URL pertenece a un conjunto de endpoints de datos o cuando la
    cabecera `Accept` indica explícitamente `application/json`.

    Args:
        request: Objeto request actual de Django.

    Returns:
        bool: `True` si la respuesta debería devolverse como JSON.
    """
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", "") or ""

    if request.method != "GET":
        return True

    if url_name in JSON_URL_NAMES:
        return True

    accept_header = request.headers.get("Accept", "")
    return "application/json" in accept_header.lower()


def _build_unauthorized_response(request, message: str):
    """
    Construye la respuesta apropiada para un acceso no autenticado.

    Si la petición espera JSON, se devuelve una respuesta de error con código
    `401`. En caso contrario, se redirige al formulario de login conservando la
    URL de destino en el parámetro `next`.

    Args:
        request: Objeto request actual de Django.
        message (str): Mensaje descriptivo del motivo del rechazo.

    Returns:
        _type_: Respuesta JSON o redirección HTTP según el tipo de petición.
    """
    if _wants_json_response(request):
        return get_error_response(message, status=401)

    login_url = reverse("auth_app:login")
    return HttpResponseRedirect(f"{login_url}?next={request.get_full_path()}")


def _build_forbidden_response(request, message: str):
    """
    Construye la respuesta apropiada cuando el usuario no tiene permisos.

    Para endpoints de datos se devuelve JSON con código `403`. Para ciertas
    vistas HTML se redirige al inicio, y para el resto se genera una respuesta
    `HttpResponseForbidden`.

    Args:
        request: Objeto request actual de Django.
        message (str): Mensaje que describe la restricción de acceso.

    Returns:
        _type_: Respuesta de error adaptada al contexto de la petición.
    """
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", "") or ""

    if _wants_json_response(request):
        return get_error_response(message, status=403)

    if url_name in HTML_REDIRECT_URL_NAMES:
        return HttpResponseRedirect(reverse("home"))

    return HttpResponseForbidden(message)


def get_request_access_profile(request) -> dict[str, set[str]]:
    """
    Recupera el perfil de acceso asociado a la petición actual.

    Este perfil contiene los roles y permisos del usuario autenticado y se
    guarda temporalmente en la request para evitar consultas repetidas dentro
    del mismo ciclo de petición.

    Args:
        request: Objeto request actual de Django.

    Returns:
        dict[str, set[str]]: Diccionario con las claves `role_codes` y
        `permission_codes`.
    """
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
    """
    Devuelve los códigos de rol disponibles para la petición actual.

    Args:
        request: Objeto request actual de Django.

    Returns:
        set[str]: Conjunto de códigos de rol asociados al usuario.
    """
    return set(get_request_access_profile(request).get("role_codes", set()))


def get_request_permission_codes(request) -> set[str]:
    """
    Devuelve los códigos de permiso disponibles para la petición actual.

    Args:
        request: Objeto request actual de Django.

    Returns:
        set[str]: Conjunto de permisos asociados al usuario autenticado.
    """
    return set(get_request_access_profile(request).get("permission_codes", set()))


def user_has_role(request, *role_codes: str) -> bool:
    """
    Comprueba si el usuario tiene al menos uno de los roles indicados.

    Args:
        request: Objeto request actual de Django.
        *role_codes (str): Códigos de rol que se desean validar.

    Returns:
        bool: `True` si el usuario posee alguno de los roles solicitados.
    """
    normalized_codes = _normalize_codes(*role_codes)
    if not normalized_codes:
        return False

    if _is_superuser(request):
        return True

    user_role_codes = get_request_role_codes(request)
    return any(code in user_role_codes for code in normalized_codes)


def user_has_permission(request, *permission_codes: str, require_all: bool = False) -> bool:
    """
    Comprueba si el usuario tiene uno o varios permisos determinados.

    Args:
        request: Objeto request actual de Django.
        *permission_codes (str): Permisos que se desean validar.
        require_all (bool): Si vale `True`, exige que todos los permisos estén
            presentes. Si vale `False`, basta con que exista uno de ellos.

    Returns:
        bool: Resultado de la comprobación de permisos.
    """
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
    """
    Protege una vista para que solo pueda ejecutarse con sesión autenticada.

    Args:
        view_func (Callable): Vista que será envuelta por el decorador.

    Returns:
        Callable: Función decorada que valida autenticación antes de continuar.
    """
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
    """
    Crea un decorador que restringe el acceso a superusuarios.

    Args:
        message (str | None): Mensaje personalizado a mostrar cuando el acceso
            no esté permitido.

    Returns:
        Callable: Decorador listo para aplicarse sobre una vista.
    """
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


def require_role(*role_codes: str, message: str | None = None):
    """
    Crea un decorador que exige al menos uno de los roles indicados.

    Args:
        *role_codes (str): Roles válidos para acceder al recurso.
        message (str | None): Mensaje personalizado para el caso de acceso
            denegado.

    Returns:
        Callable: Decorador aplicable sobre vistas.
    """
    normalized_codes = _normalize_codes(*role_codes)

    def decorator(view_func: Callable):
        @wraps(view_func)
        @require_app_session
        def wrapper(request, *args, **kwargs):
            if not normalized_codes:
                return view_func(request, *args, **kwargs)

            if user_has_role(request, *normalized_codes):
                return view_func(request, *args, **kwargs)

            final_message = message or "No tienes el rol necesario para acceder a este recurso"
            return _build_forbidden_response(request, final_message)

        return wrapper

    return decorator


def require_any_role(*role_codes: str, message: str | None = None):
    """
    Alias semántico de `require_role`.

    Se mantiene para mejorar la legibilidad cuando la intención es expresar de
    forma explícita que basta con tener cualquiera de los roles enviados.

    Args:
        *role_codes (str): Roles aceptados.
        message (str | None): Mensaje personalizado de acceso denegado.

    Returns:
        Callable: Decorador de control de acceso por roles.
    """
    return require_role(*role_codes, message=message)


def require_permission(*permission_codes: str, require_all: bool = False, message: str | None = None):
    """
    Crea un decorador que exige permisos para acceder a una vista.

    Args:
        *permission_codes (str): Permisos requeridos para acceder al recurso.
        require_all (bool): Si vale `True`, obliga a poseer todos los permisos.
            Si vale `False`, basta con poseer uno de ellos.
        message (str | None): Mensaje de error personalizado.

    Returns:
        Callable: Decorador aplicable sobre vistas protegidas por permisos.
    """
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
    """
    Alias semántico de `require_permission` para escenarios de coincidencia parcial.

    Args:
        *permission_codes (str): Permisos válidos para acceder.
        message (str | None): Mensaje personalizado de acceso denegado.

    Returns:
        Callable: Decorador de validación por permisos.
    """
    return require_permission(*permission_codes, require_all=False, message=message)


def build_crud_permission_map(permission_prefix: str) -> dict[str, tuple[str, ...]]:
    """
    Construye el mapa estándar de permisos CRUD para una entidad.

    A partir de un prefijo, por ejemplo `DOCUMENT`, se generan automáticamente
    los permisos esperados para listar, crear, editar y eliminar.

    Args:
        permission_prefix (str): Prefijo base a partir del cual se crearán los
            códigos de permiso.

    Returns:
        dict[str, tuple[str, ...]]: Mapa que relaciona cada vista CRUD con los
        permisos necesarios para poder ejecutarla.
    """
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

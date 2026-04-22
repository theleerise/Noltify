"""
Utilidades para gestionar la sesión autenticada de la aplicación.

Este módulo concentra las funciones necesarias para construir la estructura del
usuario en sesión, iniciar sesión, cerrarla y comprobar si la petición actual
tiene un usuario autenticado.
"""

from __future__ import annotations

from typing import Any


SESSION_USER_KEY = "auth_app_user"


def build_session_user(record: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Construye el diccionario de usuario que se guardará en la sesión.

    Se extraen únicamente los campos necesarios para trabajar con autenticación
    y autorización dentro de la aplicación.

    Args:
        record (dict[str, Any] | None): Registro completo del usuario obtenido
            desde base de datos.

    Returns:
        dict[str, Any] | None: Diccionario resumido con la información del
        usuario o `None` si no se recibió un registro válido.
    """
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
    """
    Inicia la sesión del usuario dentro de la aplicación.

    Además de guardar los datos mínimos del usuario en la sesión, este método
    rota la clave de sesión para reforzar la seguridad y deja el usuario
    disponible en `request.app_user`.

    Args:
        request: Objeto request actual de Django.
        record (dict[str, Any]): Registro del usuario autenticado.

    Returns:
        dict[str, Any]: Diccionario de usuario que finalmente se guarda en
        sesión.
    """
    session_user = build_session_user(record) or {}
    request.session.cycle_key()
    request.session[SESSION_USER_KEY] = session_user
    request.app_user = session_user
    return session_user


def logout_app_user(request) -> None:
    """
    Elimina de la sesión al usuario autenticado de la aplicación.

    Args:
        request: Objeto request actual de Django.

    Returns:
        None: El usuario queda eliminado de la sesión activa.
    """
    request.session.pop(SESSION_USER_KEY, None)
    request.app_user = None


def get_session_user(request) -> dict[str, Any] | None:
    """
    Obtiene el usuario autenticado almacenado en la sesión actual.

    Args:
        request: Objeto request actual de Django.

    Returns:
        dict[str, Any] | None: Datos del usuario autenticado o `None` si no
        existe una sesión válida.
    """
    return request.session.get(SESSION_USER_KEY)


def is_authenticated(request) -> bool:
    """
    Comprueba si la petición actual pertenece a un usuario autenticado.

    Args:
        request: Objeto request actual de Django.

    Returns:
        bool: `True` si existe un usuario en sesión con identificador válido.
    """
    session_user = get_session_user(request)
    return bool(session_user and session_user.get("id"))

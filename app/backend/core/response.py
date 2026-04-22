"""Helpers for parsing request bodies and building JSON API responses."""

import json

from django.http import JsonResponse


def get_request_json(request) -> dict:
    """
    Obtiene el body JSON de la request.
    Si no existe o viene vacÃ­o, devuelve {}.
    """
    try:
        if not request.body:
            return {}
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def get_success_response(data=None, message: str = "OperaciÃ³n realizada correctamente", status: int = 200):
    """Build a standard successful JSON response payload."""
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status
    )


def get_error_response(error: str, status: int = 500, data=None):
    """Build a standard error JSON response payload."""
    return JsonResponse(
        {
            "success": False,
            "error": error,
            "data": data,
        },
        status=status
    )

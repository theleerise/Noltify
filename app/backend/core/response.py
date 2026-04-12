import json

from django.http import JsonResponse


def get_request_json(request) -> dict:
    """
    Obtiene el body JSON de la request.
    Si no existe o viene vacío, devuelve {}.
    """
    try:
        if not request.body:
            return {}
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def get_success_response(data=None, message: str = "Operación realizada correctamente", status: int = 200):
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status
    )


def get_error_response(error: str, status: int = 500, data=None):
    return JsonResponse(
        {
            "success": False,
            "error": error,
            "data": data,
        },
        status=status
    )

"""
Utilidades para procesar cuerpos JSON y construir respuestas estándar.

Este módulo reúne funciones auxiliares utilizadas por las vistas para leer el
contenido JSON de una petición y devolver respuestas homogéneas de éxito o
error.
"""

import json

from django.http import JsonResponse


def get_request_json(request) -> dict:
    """
    Obtiene el contenido JSON enviado en el cuerpo de la petición.

    Si la petición no contiene cuerpo o el contenido no puede interpretarse
    correctamente como JSON, el método devuelve un diccionario vacío para evitar
    que la vista falle por este motivo.

    Args:
        request: Objeto request actual de Django.

    Returns:
        dict: Diccionario con los datos decodificados desde el body o `{}` si no
        existe contenido válido.
    """
    try:
        if not request.body:
            return {}
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def get_success_response(data=None, message: str = "Operación realizada correctamente", status: int = 200):
    """
    Construye una respuesta JSON estándar para operaciones exitosas.

    Args:
        data: Información adicional que se incluirá en la respuesta.
        message (str): Mensaje descriptivo del resultado exitoso.
        status (int): Código HTTP que se devolverá en la respuesta.

    Returns:
        JsonResponse: Respuesta JSON con la estructura estándar de éxito de la
        aplicación.
    """
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status
    )


def get_error_response(error: str, status: int = 500, data=None):
    """
    Construye una respuesta JSON estándar para operaciones con error.

    Args:
        error (str): Mensaje descriptivo del error ocurrido.
        status (int): Código HTTP que represetará el tipo de error.
        data: Información adicional relacionada con el error.

    Returns:
        JsonResponse: Respuesta JSON con la estructura estándar de error de la
        aplicación.
    """
    return JsonResponse(
        {
            "success": False,
            "error": error,
            "data": data,
        },
        status=status
    )

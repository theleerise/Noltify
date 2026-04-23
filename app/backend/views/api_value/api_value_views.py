"""
Vistas relacionadas con api value.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_app_session
from backend.core.response import *
from backend.managers.api_value_manager import ApiValueManager
from backend.models.api_value_model import ApiValueModel

@require_http_methods(["GET"])
@require_app_session
def data(request, master):
    """
    Procesa la petición asociada a `data`.

    La función valida la entrada necesaria y devuelve la respuesta HTTP correspondiente segn el contexto de negocio.

    Args:
        request: Objeto request actual de Django.
        master: Valor de entrada utilizado por la operación.

    Returns:
        _type_: Respuesta HTTP o JSON generada para la petición actual.
    """
    try:
        request_data = request.GET.dict()

        raw_filters = request_data.get("filters", "{}")
        filters = json.loads(raw_filters) if raw_filters else {}
        raw_orders = request_data.get("orders", "{}")
        orders = json.loads(raw_orders) if raw_orders else {}
        page = int(request_data.get("page", 1))
        
        mgr = ApiValueManager()
        master_query = mgr.get_master(master)
        records = mgr.get_list(
            sql=master_query,
            params=filters,
            order_by=orders,
            data_model=False
        )

        return JsonResponse(records, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
@require_app_session
def data_page(request, master):
    """
    Realiza la operación definida por `data_page`.

    Este método encapsula la lógica principal asociada a este punto del flujo de la aplicación.

    Args:
        request: Objeto request actual de Django.
        master: Valor de entrada utilizado por la operación.

    Returns:
        _type_: Resultado generado por la operación ejecutada.
    """
    try:
        request_data = request.GET.dict()

        raw_filters = request_data.get("filters", "{}")
        filters = json.loads(raw_filters) if raw_filters else {}
        raw_orders = request_data.get("orders", "{}")
        orders = json.loads(raw_orders) if raw_orders else {}
        page = int(request_data.get("page", 1))
        
        mgr = ApiValueManager()
        master_query = mgr.get_master(master)
        records = mgr.get_list_page(
            sql=master_query,
            params=filters,
            order_by=orders,
            page=page,
            data_model=False
        )

        return JsonResponse(records, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))

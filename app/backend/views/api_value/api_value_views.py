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

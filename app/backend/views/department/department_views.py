import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from backend.managers.department_manager import DepartmentManager
from backend.models.department_model import DepartmentModel

@require_http_methods(["GET"])
def list_view(request):
    
    context_page = {
        "entity_model": json.dumps(DepartmentModel.config())
    }
    return render(
        request,
        "department/list.html",
        context_page
    )

@require_http_methods(["GET"])
def data(request):
    try:
        request_data = request.GET.dict()
        filters = request_data.get("filters", {})
        page = request_data.get("page", 1)

        mgr = DepartmentManager()
        records = mgr.get_list_page(params=filters, page=int(page), data_model=False)

        return JsonResponse(records, status=200)

    except Exception as e:
        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.response import *
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
def form_view(request):
    """
    Devuelve el HTML del formulario para ser cargado dentro del modal.
    """
    context_page = {
        "entity_model": DepartmentModel.config()
    }
    return render(
        request,
        "department/form.html",
        context_page
    )


@require_http_methods(["GET"])
def data(request):
    try:
        request_data = request.GET.dict()

        raw_filters = request_data.get("filters", "{}")
        filters = json.loads(raw_filters) if raw_filters else {}
        page = int(request_data.get("page", 1))

        mgr = DepartmentManager()
        records = mgr.get_list_page(
            params=filters,
            page=page,
            data_model=False
        )

        return JsonResponse(records, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
def new_view(request):
    """
    Devuelve la estructura base de un nuevo registro.
    Útil para precargar defaults en frontend si hiciera falta.
    """
    try:
        model_data = DepartmentModel.to_json_default_dict()
        return get_success_response(
            data=model_data,
            message="Datos iniciales obtenidos correctamente"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
def edit_view(request, id: int):
    try:
        mgr = DepartmentManager()

        record = mgr.get_by_id(
            record_id=id,
            data_model=False
        )

        if not record:
            return get_error_response(
                error="No se encontró el departamento solicitado",
                status=404
            )

        if isinstance(record, DepartmentModel):
            record = record.to_json_dict()
        else:
            record = DepartmentModel.serialize_record(record)

        return get_success_response(
            data=record,
            message="Registro obtenido correctamente"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["POST"])
def create_view(request):
    """
    Crea un nuevo departamento.
    """
    try:
        request_data = get_request_json(request)
        data = request_data.get("data", {})
        model = DepartmentModel(**data)

        mgr = DepartmentManager()
        result = mgr.insert_query(
            model.to_insert_dict()
        )

        return get_success_response(
            data=result,
            message="Departamento creado correctamente",
            status=201
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
def update_view(request, id: int):

    try:
        request_data = get_request_json(request)
        data = request_data.get("data", {})
        model = DepartmentModel(**data)

        mgr = DepartmentManager()

        result = mgr.update_query(
            model.to_update_dict(include_primary_key=True)
        )

        return get_success_response(
            data=result,
            message="Departamento actualizado correctamente"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["DELETE"])
def delete_view(request, id: int):

    try:
        mgr = DepartmentManager()
        params = {mgr.primary_key: id}

        result = mgr.delete_query(params)

        return get_success_response(
            data=result,
            message="Departamento eliminado correctamente"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))
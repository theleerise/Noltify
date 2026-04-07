import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.department_manager import DepartmentManager
from backend.models.department_model import DepartmentModel


def _get_request_json(request) -> dict:
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


def _get_success_response(
    data=None,
    message: str = "Operación realizada correctamente",
    status: int = 200,
):
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status
    )


def _get_error_response(
    error: str,
    status: int = 500,
    data=None,
):
    return JsonResponse(
        {
            "success": False,
            "error": error,
            "data": data,
        },
        status=status
    )


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
        return _get_error_response(str(e))


@require_http_methods(["GET"])
def new_view(request):
    """
    Devuelve la estructura base de un nuevo registro.
    Útil para precargar defaults en frontend si hiciera falta.
    """
    try:
        model_data = DepartmentModel().to_json_dict()
        return _get_success_response(
            data=model_data,
            message="Datos iniciales obtenidos correctamente"
        )
    except Exception as e:
        return _get_error_response(str(e))


@require_http_methods(["GET"])
def edit_view(request, id: int):
    try:
        mgr = DepartmentManager()

        print("ANTES DE GET_BY_ID")
        print("ID:", id)

        record = mgr.get_by_id(
            record_id=id,
            data_model=False
        )

        print("RECORD DEVUELTO:", record)
        print("TIPO RECORD:", type(record))

        if not record:
            return _get_error_response(
                error="No se encontró el departamento solicitado",
                status=404
            )

        if isinstance(record, DepartmentModel):
            record = record.to_json_dict()
        else:
            record = DepartmentModel.serialize_record(record)

        return _get_success_response(
            data=record,
            message="Registro obtenido correctamente"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return _get_error_response(str(e))


@require_http_methods(["POST"])
def create_view(request):
    """
    Crea un nuevo departamento.
    """
    try:
        request_data = _get_request_json(request)
        data = request_data.get("data", {})

        model = DepartmentModel(**data)

        mgr = DepartmentManager()
        result = mgr.create(
            params=model.to_insert_dict()
        )

        return _get_success_response(
            data=result,
            message="Departamento creado correctamente",
            status=201
        )

    except Exception as e:
        return _get_error_response(str(e))


@require_http_methods(["PUT"])
def update_view(request, id: int):

    try:
        request_data = _get_request_json(request)
        data = request_data.get("data", {})

        model = DepartmentModel(**data)

        mgr = DepartmentManager()

        result = mgr.update(
            id,
            model.to_update_dict()
        )

        return _get_success_response(
            data=result,
            message="Departamento actualizado correctamente"
        )

    except Exception as e:
        return _get_error_response(str(e))


@require_http_methods(["DELETE"])
def delete_view(request, id: int):

    try:
        mgr = DepartmentManager()

        result = mgr.delete(id)

        return _get_success_response(
            data=result,
            message="Departamento eliminado correctamente"
        )

    except Exception as e:
        return _get_error_response(str(e))
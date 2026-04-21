import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission, user_has_permission
from backend.managers.document_manager import DocumentManager
from backend.models.document_department_model import DocumentDepartmentModel
from backend.models.document_model import DocumentModel
from backend.models.document_user_model import DocumentUserModel
from backend.core.response import get_error_response, get_request_json, get_success_response
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DocumentManager,
    model_class=DocumentModel,
    template_prefix="document",
    singular_name="Documento",
    created_message="Documento creado correctamente",
    updated_message="Documento actualizado correctamente",
    deleted_message="Documento eliminado correctamente",
    not_found_message="No se encontro el documento solicitado",
    permission_prefix="DOCUMENT",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
delete = _views["delete"]


@require_http_methods(["GET"])
@require_any_permission("DOCUMENT_LIST", "DOCUMENT_INSERT", "DOCUMENT_UPDATE")
def form_view(request):
    form_variant = (request.GET.get("variant") or "admin").strip().lower()
    entity_model = DocumentModel.config()
    entity_model["uploaded_by"]["hidden_form"] = True

    context_page = {
        "entity_model": entity_model,
        "entity_model_document_user": json.dumps(DocumentUserModel.config()),
        "entity_model_document_department": json.dumps(DocumentDepartmentModel.config()),
        "show_assignment_tabs": form_variant == "admin",
    }
    return render(request, "document/form.html", context_page)


def _get_multipart_document_data(request) -> dict:
    raw_data = request.POST.get("data", "{}")

    try:
        data = json.loads(raw_data) if raw_data else {}
    except json.JSONDecodeError:
        data = {}

    uploaded_file = request.FILES.get("file_binary")
    if uploaded_file is not None:
        data["file_binary"] = uploaded_file.read()
        data["file_name"] = uploaded_file.name
        data["mime_type"] = uploaded_file.content_type or None
        data["file_size"] = uploaded_file.size

    return data


def _get_current_user_id(request) -> int | None:
    session_user = getattr(request, "app_user", None) or {}

    try:
        return int(session_user.get("id"))
    except (TypeError, ValueError):
        return None


def _get_general_scope(request) -> str:
    return (request.GET.get("scope") or "").strip().lower()


def _get_document_request_data(request) -> dict:
    content_type = request.content_type or ""

    if content_type.startswith("multipart/form-data"):
        return _get_multipart_document_data(request)

    request_data = get_request_json(request)
    return request_data.get("data", {})


@require_http_methods(["POST"])
@require_any_permission("DOCUMENT_INSERT")
def create(request):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        data = _get_document_request_data(request)
        data["uploaded_by"] = current_user_id
        model = DocumentModel(**data)

        mgr = DocumentManager()
        result = mgr.insert_query(model.to_insert_dict())

        return get_success_response(
            data=result,
            message="Documento creado correctamente",
            status=201,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
@require_any_permission("DOCUMENT_UPDATE")
def update(request, id: int):
    try:
        mgr = DocumentManager()
        existing_record = mgr.get_by_id(record_id=id, data_model=False)

        if not existing_record:
            return get_error_response(error="No se encontro el documento solicitado", status=404)

        data = _get_document_request_data(request)
        data["id"] = id
        data["file_name"] = existing_record.get("file_name")
        data["mime_type"] = existing_record.get("mime_type")
        data["file_size"] = existing_record.get("file_size")
        data["uploaded_by"] = existing_record.get("uploaded_by")

        if data.get("is_active") is None:
            data["is_active"] = existing_record.get("is_active", True)

        model = DocumentModel(**data)
        result = mgr.update_query(model.to_update_dict(include_primary_key=True))

        return get_success_response(
            data=result,
            message="Documento actualizado correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
@require_any_permission("DOCUMENT_LIST")
def document_file(request, id: int):
    try:
        mgr = DocumentManager()
        session_user = getattr(request, "app_user", None) or {}
        current_user_id = _get_current_user_id(request)
        document = (
            mgr.get_document(id)
            if bool(session_user.get("is_superuser"))
            else mgr.get_accessible_document(id, current_user_id or 0)
        )

        if not document:
            return get_error_response(error="No se encontro el documento solicitado", status=404)

        file_binary = document.get("file_binary")
        if not file_binary:
            return get_error_response(error="El documento no contiene archivo asociado", status=404)

        file_name = document.get("file_name") or f"documento_{id}"
        mime_type = document.get("mime_type") or "application/octet-stream"

        response = HttpResponse(file_binary, content_type=mime_type)
        response["Content-Disposition"] = f'inline; filename="{file_name}"'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
@require_any_permission("DOCUMENT_LIST")
def general_view(request):
    current_user_id = _get_current_user_id(request)
    if not current_user_id:
        return get_error_response("No se pudo identificar al usuario de sesion", status=401)

    mgr = DocumentManager()
    departments = mgr.get_user_departments(current_user_id)

    permission_flags = {
        "can_list": user_has_permission(request, "DOCUMENT_LIST"),
        "can_insert": user_has_permission(request, "DOCUMENT_INSERT"),
        "can_update": user_has_permission(request, "DOCUMENT_UPDATE"),
        "can_delete": user_has_permission(request, "DOCUMENT_DELETE"),
    }

    context_page = {
        "document_entity_model": json.dumps(DocumentModel.config()),
        "current_user_id": current_user_id,
        "user_departments": departments,
        "document_permissions": permission_flags,
        "document_permissions_json": json.dumps(permission_flags),
    }

    return render(request, "document/general.html", context_page)


@require_http_methods(["GET"])
@require_any_permission("DOCUMENT_LIST")
def general_data(request):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        scope = _get_general_scope(request)
        department_id = request.GET.get("department_id")
        raw_orders = request.GET.get("orders", "{}")
        orders = json.loads(raw_orders) if raw_orders else {}
        page = int(request.GET.get("page", 1))

        parsed_department_id = None
        if scope == "department":
            if not department_id:
                return get_error_response("Debes indicar el departamento a consultar", status=400)

            parsed_department_id = int(department_id)

        mgr = DocumentManager()

        if parsed_department_id and not mgr.user_belongs_to_department(current_user_id, parsed_department_id):
            return get_error_response("No tienes acceso al departamento indicado", status=403)

        records = mgr.get_general_documents_page(
            scope=scope,
            user_id=current_user_id,
            department_id=parsed_department_id,
            page=page,
            order_by=orders,
        )

        return JsonResponse(records, status=200)
    except ValueError as error:
        return get_error_response(str(error), status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["POST"])
@require_any_permission("DOCUMENT_INSERT")
def general_create(request):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        scope = _get_general_scope(request)
        if scope not in {"department", "user"}:
            return get_error_response("El contexto de creacion indicado no es valido", status=400)

        content_type = request.content_type or ""
        if content_type.startswith("multipart/form-data"):
            data = _get_multipart_document_data(request)
        else:
            request_data = get_request_json(request)
            data = request_data.get("data", {})

        if not data.get("file_binary"):
            return get_error_response("Debes seleccionar un archivo para crear el documento", status=400)

        data["uploaded_by"] = current_user_id
        model = DocumentModel(**data)
        mgr = DocumentManager()

        department_id = None
        if scope == "department":
            department_id_param = request.GET.get("department_id")
            if not department_id_param:
                return get_error_response("Debes indicar el departamento para crear el documento", status=400)

            department_id = int(department_id_param)
            if not mgr.user_belongs_to_department(current_user_id, department_id):
                return get_error_response("No tienes acceso al departamento indicado", status=403)

        result = mgr.create_document_for_user(
            document_data=model.to_insert_dict(),
            uploaded_by=current_user_id,
            department_id=department_id,
        )

        return get_success_response(
            data=result,
            message="Documento creado correctamente",
            status=201,
        )
    except ValueError as error:
        return get_error_response(str(error), status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
@require_any_permission("DOCUMENT_UPDATE")
def general_update(request, id: int):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        mgr = DocumentManager()
        existing_record = mgr.get_owned_document(document_id=id, uploaded_by=current_user_id)

        if not existing_record:
            return get_error_response("No tienes permisos para editar este documento", status=403)

        request_data = get_request_json(request)
        data = request_data.get("data", {})
        data["id"] = id
        data["uploaded_by"] = existing_record.get("uploaded_by")
        data["file_name"] = existing_record.get("file_name")
        data["mime_type"] = existing_record.get("mime_type")
        data["file_size"] = existing_record.get("file_size")
        data["is_active"] = existing_record.get("is_active", True)

        model = DocumentModel(**data)
        result = mgr.update_query(model.to_update_dict(include_primary_key=True))

        return get_success_response(
            data=result,
            message="Documento actualizado correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["DELETE"])
@require_any_permission("DOCUMENT_DELETE")
def general_delete(request, id: int):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        mgr = DocumentManager()
        existing_record = mgr.get_owned_document(document_id=id, uploaded_by=current_user_id)

        if not existing_record:
            return get_error_response("No tienes permisos para eliminar este documento", status=403)

        result = mgr.delete_query({"id": id})

        return get_success_response(
            data=result,
            message="Documento eliminado correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))

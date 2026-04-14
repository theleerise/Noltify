import json

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from backend.managers.document_manager import DocumentManager
from backend.models.document_model import DocumentModel
from backend.core.response import get_error_response, get_request_json, get_success_response
from backend.views.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DocumentManager,
    model_class=DocumentModel,
    template_prefix="document",
    singular_name="Documento",
    created_message="Documento creado correctamente",
    updated_message="Documento actualizado correctamente",
    deleted_message="Documento eliminado correctamente",
    not_found_message="No se encontró el documento solicitado",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


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


@require_http_methods(["POST"])
def create(request):
    try:
        content_type = request.content_type or ""
        if content_type.startswith("multipart/form-data"):
            data = _get_multipart_document_data(request)
        else:
            request_data = get_request_json(request)
            data = request_data.get("data", {})

        if not data.get("file_binary"):
            return get_error_response("Debes seleccionar un archivo para crear el documento", status=400)

        model = DocumentModel(**data)

        mgr = DocumentManager()
        result = mgr.insert_query(model.to_insert_dict())

        return get_success_response(
            data=result,
            message="Documento creado correctamente",
            status=201
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
def update(request, id: int):
    try:
        request_data = get_request_json(request)
        data = request_data.get("data", {})

        mgr = DocumentManager()
        existing_record = mgr.get_by_id(record_id=id, data_model=False)

        if not existing_record:
            return get_error_response(error="No se encontró el documento solicitado", status=404)

        data["id"] = id
        data["file_name"] = existing_record.get("file_name")
        data["mime_type"] = existing_record.get("mime_type")
        data["file_size"] = existing_record.get("file_size")

        model = DocumentModel(**data)
        result = mgr.update_query(model.to_update_dict(include_primary_key=True))

        return get_success_response(
            data=result,
            message="Documento actualizado correctamente"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
def document_file(request, id: int):
    try:
        mgr = DocumentManager()
        document = mgr.get_document(id)

        if not document:
            return get_error_response(error="No se encontró el documento solicitado", status=404)

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

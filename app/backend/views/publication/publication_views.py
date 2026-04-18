import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission, user_has_permission
from backend.core.response import get_error_response, get_request_json, get_success_response
from backend.managers.publication_manager import PublicationManager
from backend.models.publication_department_model import PublicationDepartmentModel
from backend.models.publication_model import PublicationModel
from backend.models.publication_user_model import PublicationUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationManager,
    model_class=PublicationModel,
    template_prefix="publication",
    singular_name="Publicacion",
    created_message="Publicacion creada correctamente",
    updated_message="Publicacion actualizada correctamente",
    deleted_message="Publicacion eliminada correctamente",
    not_found_message="No se encontro la publicacion solicitada",
    permission_prefix="PUBLICATION",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
@require_any_permission("PUBLICATION_LIST", "PUBLICATION_INSERT", "PUBLICATION_UPDATE")
def form_view(request):
    form_variant = (request.GET.get("variant") or "admin").strip().lower()
    entity_model = PublicationModel.config()

    if form_variant in {"user", "department", "viewer"}:
        entity_model["created_by"]["hidden_form"] = True

    if form_variant == "viewer":
        for field_name in ("title", "content", "status", "is_active"):
            if field_name in entity_model:
                entity_model[field_name]["readonly"] = True

    context_page = {
        "entity_model": entity_model,
        "entity_model_publication_user": json.dumps(PublicationUserModel.config()),
        "entity_model_publication_department": json.dumps(PublicationDepartmentModel.config()),
        "show_assignment_tabs": form_variant == "admin",
    }
    return render(request, "publication/form.html", context_page)


def _get_current_user_id(request) -> int | None:
    session_user = getattr(request, "app_user", None) or {}

    try:
        return int(session_user.get("id"))
    except (TypeError, ValueError):
        return None


def _get_general_scope(request) -> str:
    return (request.GET.get("scope") or "").strip().lower()


@require_http_methods(["GET"])
@require_any_permission("PUBLICATION_LIST")
def general_view(request):
    current_user_id = _get_current_user_id(request)
    if not current_user_id:
        return get_error_response("No se pudo identificar al usuario de sesion", status=401)

    mgr = PublicationManager()
    departments = mgr.get_user_departments(current_user_id)
    session_user = getattr(request, "app_user", None) or {}

    permission_flags = {
        "can_list": user_has_permission(request, "PUBLICATION_LIST"),
        "can_insert": user_has_permission(request, "PUBLICATION_INSERT"),
        "can_update": user_has_permission(request, "PUBLICATION_UPDATE"),
        "can_delete": user_has_permission(request, "PUBLICATION_DELETE"),
    }

    context_page = {
        "publication_entity_model": json.dumps(PublicationModel.config()),
        "current_user_id": current_user_id,
        "current_user_is_superuser": bool(session_user.get("is_superuser")),
        "user_departments": departments,
        "publication_permissions": permission_flags,
        "publication_permissions_json": json.dumps(permission_flags),
    }

    return render(request, "publication/general.html", context_page)


@require_http_methods(["GET"])
@require_any_permission("PUBLICATION_LIST")
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

        mgr = PublicationManager()

        if parsed_department_id and not mgr.user_belongs_to_department(current_user_id, parsed_department_id):
            return get_error_response("No tienes acceso al departamento indicado", status=403)

        records = mgr.get_general_publications_page(
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
@require_any_permission("PUBLICATION_INSERT")
def general_create(request):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        scope = _get_general_scope(request)
        if scope not in {"department", "user"}:
            return get_error_response("El contexto de creacion indicado no es valido", status=400)

        request_data = get_request_json(request)
        data = request_data.get("data", {})
        model = PublicationModel(**data)
        mgr = PublicationManager()

        department_id = None
        if scope == "department":
            department_id_param = request.GET.get("department_id")
            if not department_id_param:
                return get_error_response("Debes indicar el departamento para crear la publicacion", status=400)

            department_id = int(department_id_param)
            if not mgr.user_belongs_to_department(current_user_id, department_id):
                return get_error_response("No tienes acceso al departamento indicado", status=403)

        result = mgr.create_publication_for_user(
            publication_data=model.to_insert_dict(),
            created_by=current_user_id,
            department_id=department_id,
        )

        return get_success_response(
            data=result,
            message="Publicacion creada correctamente",
            status=201,
        )
    except ValueError as error:
        return get_error_response(str(error), status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
@require_any_permission("PUBLICATION_UPDATE")
def general_update(request, id: int):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        session_user = getattr(request, "app_user", None) or {}
        is_superuser = bool(session_user.get("is_superuser"))
        mgr = PublicationManager()
        existing_record = (
            mgr.get_by_id(record_id=id, data_model=False)
            if is_superuser
            else mgr.get_owned_publication(publication_id=id, created_by=current_user_id)
        )

        if not existing_record:
            return get_error_response("No tienes permisos para editar esta publicacion", status=403)

        request_data = get_request_json(request)
        data = request_data.get("data", {})
        data["id"] = id
        data["created_by"] = existing_record.get("created_by", current_user_id)
        data["is_active"] = existing_record.get("is_active", True)

        model = PublicationModel(**data)
        result = mgr.update_query(model.to_update_dict(include_primary_key=True))

        return get_success_response(
            data=result,
            message="Publicacion actualizada correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["DELETE"])
@require_any_permission("PUBLICATION_DELETE")
def general_delete(request, id: int):
    try:
        current_user_id = _get_current_user_id(request)
        if not current_user_id:
            return get_error_response("No se pudo identificar al usuario de sesion", status=401)

        session_user = getattr(request, "app_user", None) or {}
        is_superuser = bool(session_user.get("is_superuser"))
        mgr = PublicationManager()
        existing_record = (
            mgr.get_by_id(record_id=id, data_model=False)
            if is_superuser
            else mgr.get_owned_publication(publication_id=id, created_by=current_user_id)
        )

        if not existing_record:
            return get_error_response("No tienes permisos para eliminar esta publicacion", status=403)

        result = mgr.delete_query({"id": id})

        return get_success_response(
            data=result,
            message="Publicacion eliminada correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))

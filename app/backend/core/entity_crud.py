"""Factory helpers for building standard CRUD views from managers and models."""

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import build_crud_permission_map, require_any_permission
from backend.core.response import get_error_response, get_request_json, get_success_response


def build_crud_views(
    *,
    manager_class,
    model_class,
    template_prefix: str,
    singular_name: str,
    created_message: str,
    updated_message: str,
    deleted_message: str,
    not_found_message: str,
    permission_prefix: str | None = None,
):
    """Build the default CRUD view set for a model-manager pair."""

    @require_http_methods(["GET"])
    def list_view(request):
        """Render the list template for the entity."""
        context_page = {
            "entity_model": json.dumps(model_class.config())
        }
        return render(request, f"{template_prefix}/list.html", context_page)

    @require_http_methods(["GET"])
    def form_view(request):
        """Render the form template for the entity."""
        context_page = {
            "entity_model": model_class.config()
        }
        return render(request, f"{template_prefix}/form.html", context_page)

    @require_http_methods(["GET"])
    def data(request):
        """Return paginated records for the entity as JSON."""
        try:
            request_data = request.GET.dict()

            raw_filters = request_data.get("filters", "{}")
            filters = json.loads(raw_filters) if raw_filters else {}
            raw_orders = request_data.get("orders", "{}")
            orders = json.loads(raw_orders) if raw_orders else {}
            page = int(request_data.get("page", 1))

            mgr = manager_class()
            records = mgr.get_list_page(
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

    @require_http_methods(["GET"])
    def new_view(request):
        """Return the default payload used to initialize a creation form."""
        try:
            model_data = model_class.to_json_default_dict()
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
        """Return the serialized record required to edit one entity instance."""
        try:
            mgr = manager_class()
            record = mgr.get_by_id(record_id=id, data_model=False)

            if not record:
                return get_error_response(error=not_found_message, status=404)

            if isinstance(record, model_class):
                record = record.to_json_dict()
            else:
                record = model_class.serialize_record(record)

            return get_success_response(
                data=record,
                message=f"{singular_name} obtenido correctamente"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["POST"])
    def create(request):
        """Create a new entity instance from the request payload."""
        try:
            request_data = get_request_json(request)
            data = request_data.get("data", {})
            model = model_class(**data)

            mgr = manager_class()
            result = mgr.insert_query(model.to_insert_dict())

            return get_success_response(
                data=result,
                message=created_message,
                status=201
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["PUT"])
    def update(request, id: int):
        """Update an existing entity instance from the request payload."""
        try:
            request_data = get_request_json(request)
            data = request_data.get("data", {})
            data["id"] = id
            model = model_class(**data)

            mgr = manager_class()
            result = mgr.update_query(model.to_update_dict(include_primary_key=True))

            return get_success_response(
                data=result,
                message=updated_message
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["DELETE"])
    def delete(request, id: int):
        """Delete an entity instance by its identifier."""
        try:
            mgr = manager_class()
            params = {mgr.primary_key: id}
            result = mgr.delete_query(params)

            return get_success_response(
                data=result,
                message=deleted_message
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    views = {
        "list_view": list_view,
        "form_view": form_view,
        "data": data,
        "new_view": new_view,
        "edit_view": edit_view,
        "create": create,
        "update": update,
        "delete": delete,
    }

    if not permission_prefix:
        return views

    permission_map = build_crud_permission_map(permission_prefix)

    for view_name, permission_codes in permission_map.items():
        views[view_name] = require_any_permission(*permission_codes)(views[view_name])

    return views

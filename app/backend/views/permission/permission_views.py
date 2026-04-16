import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.permission_manager import PermissionManager
from backend.models.permission_model import PermissionModel
from backend.models.permission_user_model import PermissionUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PermissionManager,
    model_class=PermissionModel,
    template_prefix="permission",
    singular_name="Permiso",
    created_message="Permiso creado correctamente",
    updated_message="Permiso actualizado correctamente",
    deleted_message="Permiso eliminado correctamente",
    not_found_message="No se encontró el permiso solicitado",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
def form_view(request):
    context_page = {
        "entity_model": PermissionModel.config(),
        "entity_model_permission_user": json.dumps(PermissionUserModel.config()),
    }
    return render(request, "permission/form.html", context_page)

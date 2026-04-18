import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission
from backend.managers.role_manager import RoleManager
from backend.models.role_model import RoleModel
from backend.models.role_permission_model import RolePermissionModel
from backend.models.role_user_model import RoleUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RoleManager,
    model_class=RoleModel,
    template_prefix="role",
    singular_name="Rol",
    created_message="Rol creado correctamente",
    updated_message="Rol actualizado correctamente",
    deleted_message="Rol eliminado correctamente",
    not_found_message="No se encontro el rol solicitado",
    permission_prefix="ROLE",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
@require_any_permission("ROLE_LIST", "ROLE_INSERT", "ROLE_UPDATE")
def form_view(request):
    context_page = {
        "entity_model": RoleModel.config(),
        "entity_model_role_user": json.dumps(RoleUserModel.config()),
        "entity_model_role_permission": json.dumps(RolePermissionModel.config()),
    }
    return render(request, "role/form.html", context_page)

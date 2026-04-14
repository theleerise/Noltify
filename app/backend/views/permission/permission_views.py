from backend.managers.permission_manager import PermissionManager
from backend.models.permission_model import PermissionModel
from backend.views.entity_crud import build_crud_views


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
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

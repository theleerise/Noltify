from backend.managers.role_permission_manager import RolePermissionManager
from backend.models.role_permission_model import RolePermissionModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RolePermissionManager,
    model_class=RolePermissionModel,
    template_prefix="role_permission",
    singular_name="Asignación rol-permiso",
    created_message="Asignación rol-permiso creada correctamente",
    updated_message="Asignación rol-permiso actualizada correctamente",
    deleted_message="Asignación rol-permiso eliminada correctamente",
    not_found_message="No se encontró la asignación rol-permiso solicitada",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

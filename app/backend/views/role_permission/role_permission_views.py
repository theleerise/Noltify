from backend.core.authorization import require_superuser
from backend.managers.role_permission_manager import RolePermissionManager
from backend.models.role_permission_model import RolePermissionModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RolePermissionManager,
    model_class=RolePermissionModel,
    template_prefix="role_permission",
    singular_name="Asignacion rol-permiso",
    created_message="Asignacion rol-permiso creada correctamente",
    updated_message="Asignacion rol-permiso actualizada correctamente",
    deleted_message="Asignacion rol-permiso eliminada correctamente",
    not_found_message="No se encontro la asignacion rol-permiso solicitada",
)

list_view = require_superuser()(_views["list_view"])
form_view = require_superuser()(_views["form_view"])
data = require_superuser()(_views["data"])
new_view = require_superuser()(_views["new_view"])
edit_view = require_superuser()(_views["edit_view"])
create = require_superuser()(_views["create"])
update = require_superuser()(_views["update"])
delete = require_superuser()(_views["delete"])

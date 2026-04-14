from backend.managers.role_manager import RoleManager
from backend.models.role_model import RoleModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RoleManager,
    model_class=RoleModel,
    template_prefix="role",
    singular_name="Rol",
    created_message="Rol creado correctamente",
    updated_message="Rol actualizado correctamente",
    deleted_message="Rol eliminado correctamente",
    not_found_message="No se encontró el rol solicitado",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

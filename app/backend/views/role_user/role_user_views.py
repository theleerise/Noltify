from backend.managers.role_user_manager import RoleUserManager
from backend.models.role_user_model import RoleUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RoleUserManager,
    model_class=RoleUserModel,
    template_prefix="role_user",
    singular_name="Asignación rol-usuario",
    created_message="Asignación rol-usuario creada correctamente",
    updated_message="Asignación rol-usuario actualizada correctamente",
    deleted_message="Asignación rol-usuario eliminada correctamente",
    not_found_message="No se encontró la asignación rol-usuario solicitada",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

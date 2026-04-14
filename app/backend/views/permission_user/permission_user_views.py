from backend.managers.permission_user_manager import PermissionUserManager
from backend.models.permission_user_model import PermissionUserModel
from backend.views.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PermissionUserManager,
    model_class=PermissionUserModel,
    template_prefix="permission_user",
    singular_name="Asignación permiso-usuario",
    created_message="Asignación permiso-usuario creada correctamente",
    updated_message="Asignación permiso-usuario actualizada correctamente",
    deleted_message="Asignación permiso-usuario eliminada correctamente",
    not_found_message="No se encontró la asignación permiso-usuario solicitada",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

from backend.managers.app_user_manager import AppUserManager
from backend.models.app_user_model import AppUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=AppUserManager,
    model_class=AppUserModel,
    template_prefix="app_user",
    singular_name="Usuario",
    created_message="Usuario creado correctamente",
    updated_message="Usuario actualizado correctamente",
    deleted_message="Usuario eliminado correctamente",
    not_found_message="No se encontró el usuario solicitado",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

from backend.managers.publication_user_manager import PublicationUserManager
from backend.models.publication_user_model import PublicationUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationUserManager,
    model_class=PublicationUserModel,
    template_prefix="publication_user",
    singular_name="Asignacion publicacion-usuario",
    created_message="Asignacion publicacion-usuario creada correctamente",
    updated_message="Asignacion publicacion-usuario actualizada correctamente",
    deleted_message="Asignacion publicacion-usuario eliminada correctamente",
    not_found_message="No se encontro la asignacion publicacion-usuario solicitada",
    permission_prefix="PUBLICATION_USER",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

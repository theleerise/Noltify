from backend.managers.publication_user_manager import PublicationUserManager
from backend.models.publication_user_model import PublicationUserModel
from backend.views.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationUserManager,
    model_class=PublicationUserModel,
    template_prefix="publication_user",
    singular_name="Asignación publicación-usuario",
    created_message="Asignación publicación-usuario creada correctamente",
    updated_message="Asignación publicación-usuario actualizada correctamente",
    deleted_message="Asignación publicación-usuario eliminada correctamente",
    not_found_message="No se encontró la asignación publicación-usuario solicitada",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

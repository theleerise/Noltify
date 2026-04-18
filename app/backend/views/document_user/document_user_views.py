from backend.managers.document_user_manager import DocumentUserManager
from backend.models.document_user_model import DocumentUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DocumentUserManager,
    model_class=DocumentUserModel,
    template_prefix="document_user",
    singular_name="Asignacion documento-usuario",
    created_message="Asignacion documento-usuario creada correctamente",
    updated_message="Asignacion documento-usuario actualizada correctamente",
    deleted_message="Asignacion documento-usuario eliminada correctamente",
    not_found_message="No se encontro la asignacion documento-usuario solicitada",
    permission_prefix="DOCUMENT_USER",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

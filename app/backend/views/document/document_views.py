from backend.managers.document_manager import DocumentManager
from backend.models.document_model import DocumentModel
from backend.views.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DocumentManager,
    model_class=DocumentModel,
    template_prefix="document",
    singular_name="Documento",
    created_message="Documento creado correctamente",
    updated_message="Documento actualizado correctamente",
    deleted_message="Documento eliminado correctamente",
    not_found_message="No se encontró el documento solicitado",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

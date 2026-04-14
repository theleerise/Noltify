from backend.managers.publication_manager import PublicationManager
from backend.models.publication_model import PublicationModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationManager,
    model_class=PublicationModel,
    template_prefix="publication",
    singular_name="Publicación",
    created_message="Publicación creada correctamente",
    updated_message="Publicación actualizada correctamente",
    deleted_message="Publicación eliminada correctamente",
    not_found_message="No se encontró la publicación solicitada",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

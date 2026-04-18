from backend.managers.publication_department_manager import PublicationDepartmentManager
from backend.models.publication_department_model import PublicationDepartmentModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationDepartmentManager,
    model_class=PublicationDepartmentModel,
    template_prefix="publication_department",
    singular_name="Asignacion publicacion-departamento",
    created_message="Asignacion publicacion-departamento creada correctamente",
    updated_message="Asignacion publicacion-departamento actualizada correctamente",
    deleted_message="Asignacion publicacion-departamento eliminada correctamente",
    not_found_message="No se encontro la asignacion publicacion-departamento solicitada",
    permission_prefix="PUBLICATION_DEPARTMENT",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

from backend.managers.document_department_manager import DocumentDepartmentManager
from backend.models.document_department_model import DocumentDepartmentModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DocumentDepartmentManager,
    model_class=DocumentDepartmentModel,
    template_prefix="document_department",
    singular_name="Asignacion documento-departamento",
    created_message="Asignacion documento-departamento creada correctamente",
    updated_message="Asignacion documento-departamento actualizada correctamente",
    deleted_message="Asignacion documento-departamento eliminada correctamente",
    not_found_message="No se encontro la asignacion documento-departamento solicitada",
    permission_prefix="DOCUMENT_DEPARTMENT",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

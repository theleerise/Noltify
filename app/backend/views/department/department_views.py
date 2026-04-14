from backend.managers.department_manager import DepartmentManager
from backend.models.department_model import DepartmentModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DepartmentManager,
    model_class=DepartmentModel,
    template_prefix="department",
    singular_name="departamento",
    created_message="departamento creado correctamente",
    updated_message="departamento actualizado correctamente",
    deleted_message="departamento eliminado correctamente",
    not_found_message="No se encontró el departamento solicitado",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

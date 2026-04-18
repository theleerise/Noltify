from backend.managers.department_user_manager import DepartmentUserManager
from backend.models.deparment_user_model import DepartmentUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=DepartmentUserManager,
    model_class=DepartmentUserModel,
    template_prefix="department_user",
    singular_name="Asignacion departamento-usuario",
    created_message="Asignacion departamento-usuario creada correctamente",
    updated_message="Asignacion departamento-usuario actualizada correctamente",
    deleted_message="Asignacion departamento-usuario eliminada correctamente",
    not_found_message="No se encontro la asignacion departamento-usuario solicitada",
    permission_prefix="DEPARTMENT_USER",
)

list_view = _views["list_view"]
form_view = _views["form_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]

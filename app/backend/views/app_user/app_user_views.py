import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.app_user_manager import AppUserManager
from backend.models.app_user_model import AppUserModel
from backend.models.deparment_user_model import DepartmentUserModel
from backend.models.document_user_model import DocumentUserModel
from backend.models.permission_user_model import PermissionUserModel
from backend.models.publication_user_model import PublicationUserModel
from backend.models.role_user_model import RoleUserModel
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
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
def form_view(request):
    context_page = {
        "entity_model": AppUserModel.config(),
        "entity_model_department_user": json.dumps(DepartmentUserModel.config()),
        "entity_model_role_user": json.dumps(RoleUserModel.config()),
        "entity_model_permission_user": json.dumps(PermissionUserModel.config()),
        "entity_model_document_user": json.dumps(DocumentUserModel.config()),
        "entity_model_publication_user": json.dumps(PublicationUserModel.config()),
    }
    return render(request, "app_user/form.html", context_page)

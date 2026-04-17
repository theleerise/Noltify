import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.app_user_manager import AppUserManager
from backend.models.app_user_model import AppUserModel
from backend.models.deparment_user_model import DepartmentUserModel
from backend.models.document_model import DocumentModel
from backend.models.document_user_model import DocumentUserModel
from backend.models.permission_user_model import PermissionUserModel
from backend.models.publication_model import PublicationModel
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


@require_http_methods(["GET"])
def profile_view(request):
    mgr = AppUserManager()
    session_user = getattr(request, "app_user", None) or {}

    profile_user = None
    profile_user_id = None

    if session_user.get("id"):
        try:
            profile_user_id = int(session_user.get("id"))
            profile_user = mgr.get_by_id(record_id=profile_user_id, data_model=False)
        except ValueError:
            profile_user = None
            profile_user_id = None

    full_name = ""
    if profile_user:
        first_name = (profile_user.get("first_name") or "").strip()
        last_name = (profile_user.get("last_name") or "").strip()
        full_name = " ".join(part for part in [first_name, last_name] if part).strip()

    context_page = {
        "profile_user": profile_user,
        "profile_user_id": profile_user_id,
        "profile_user_full_name": full_name,
        "department_user_entity_model": json.dumps(DepartmentUserModel.config()),
        "publication_entity_model": json.dumps(PublicationModel.config()),
        "document_entity_model": json.dumps(DocumentModel.config()),
    }

    return render(request, "app_user/profile.html", context_page)

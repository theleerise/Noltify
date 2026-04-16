import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.department_manager import DepartmentManager
from backend.models.department_model import DepartmentModel
from backend.models.deparment_user_model import DepartmentUserModel
from backend.models.document_department_model import DocumentDepartmentModel
from backend.models.publication_department_model import PublicationDepartmentModel
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

data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
def list_view(request):
    context_page = {
        "entity_model": json.dumps(DepartmentModel.config()),
    }
    return render(request, "department/list.html", context_page)

@require_http_methods(["GET"])
def form_view(request):
    """
    Devuelve el HTML del formulario para ser cargado dentro del modal.
    """
    context_page = {
        "entity_model": DepartmentModel.config(),
        "entity_model_department_user": json.dumps(DepartmentUserModel.config()),
        "entity_model_document_department": json.dumps(DocumentDepartmentModel.config()),
        "entity_model_publication_department": json.dumps(PublicationDepartmentModel.config()),
    }
    return render(
        request,
        "department/form.html",
        context_page
    )

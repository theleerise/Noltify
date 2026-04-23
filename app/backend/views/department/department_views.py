"""
Vistas relacionadas con department.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission
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
    not_found_message="No se encontro el departamento solicitado",
    permission_prefix="DEPARTMENT",
)

data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
create = _views["create"]
update = _views["update"]
delete = _views["delete"]


@require_http_methods(["GET"])
@require_any_permission("DEPARTMENT_LIST")
def list_view(request):
    """
    Procesa la petición asociada a `list_view`.

    La función valida la entrada necesaria y devuelve la respuesta HTTP correspondiente segn el contexto de negocio.

    Args:
        request: Objeto request actual de Django.

    Returns:
        _type_: Respuesta HTTP o JSON generada para la petición actual.
    """
    context_page = {
        "entity_model": json.dumps(DepartmentModel.config()),
    }
    return render(request, "department/list.html", context_page)


@require_http_methods(["GET"])
@require_any_permission("DEPARTMENT_LIST", "DEPARTMENT_INSERT", "DEPARTMENT_UPDATE")
def form_view(request):
    """
    Procesa la petición asociada a `form_view`.

    La función valida la entrada necesaria y devuelve la respuesta HTTP correspondiente segn el contexto de negocio.

    Args:
        request: Objeto request actual de Django.

    Returns:
        _type_: Respuesta HTTP o JSON generada para la petición actual.
    """
    context_page = {
        "entity_model": DepartmentModel.config(),
        "entity_model_department_user": json.dumps(DepartmentUserModel.config()),
        "entity_model_document_department": json.dumps(DocumentDepartmentModel.config()),
        "entity_model_publication_department": json.dumps(PublicationDepartmentModel.config()),
    }
    return render(request, "department/form.html", context_page)

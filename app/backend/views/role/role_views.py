"""
Vistas relacionadas con role.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission, require_superuser
from backend.managers.role_manager import RoleManager
from backend.models.role_model import RoleModel
from backend.models.role_permission_model import RolePermissionModel
from backend.models.role_user_model import RoleUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=RoleManager,
    model_class=RoleModel,
    template_prefix="role",
    singular_name="Rol",
    created_message="Rol creado correctamente",
    updated_message="Rol actualizado correctamente",
    deleted_message="Rol eliminado correctamente",
    not_found_message="No se encontro el rol solicitado",
    permission_prefix="ROLE",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = require_superuser()(_views["new_view"])
edit_view = require_superuser()(_views["edit_view"])
create = require_superuser()(_views["create"])
update = require_superuser()(_views["update"])
delete = require_superuser()(_views["delete"])


@require_http_methods(["GET"])
@require_superuser()
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
        "entity_model": RoleModel.config(),
        "entity_model_role_user": json.dumps(RoleUserModel.config()),
        "entity_model_role_permission": json.dumps(RolePermissionModel.config()),
    }
    return render(request, "role/form.html", context_page)

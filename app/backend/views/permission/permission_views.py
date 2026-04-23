"""
Vistas relacionadas con permission.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_any_permission, require_superuser
from backend.managers.permission_manager import PermissionManager
from backend.models.permission_model import PermissionModel
from backend.models.permission_user_model import PermissionUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PermissionManager,
    model_class=PermissionModel,
    template_prefix="permission",
    singular_name="Permiso",
    created_message="Permiso creado correctamente",
    updated_message="Permiso actualizado correctamente",
    deleted_message="Permiso eliminado correctamente",
    not_found_message="No se encontro el permiso solicitado",
    permission_prefix="PERMISSION",
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
        "entity_model": PermissionModel.config(),
        "entity_model_permission_user": json.dumps(PermissionUserModel.config()),
    }
    return render(request, "permission/form.html", context_page)

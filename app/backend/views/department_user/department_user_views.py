"""
Vistas relacionadas con department user.

Este módulo agrupa las funciones encargadas de procesar peticiones HTTP y devolver respuestas HTML o JSON para el contexto indicado.
"""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from backend.core.authorization import require_app_session
from backend.core.response import get_error_response
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


@require_http_methods(["GET"])
@require_app_session
def profile_data(request):
    """
    Realiza la operación definida por `profile_data`.

    Este método encapsula la lógica principal asociada a este punto del flujo de la aplicación.

    Args:
        request: Objeto request actual de Django.

    Returns:
        _type_: Resultado generado por la operación ejecutada.
    """
    try:
        session_user = getattr(request, "app_user", None) or {}
        current_user_id = int(session_user.get("id"))

        raw_orders = request.GET.get("orders", "{}")
        orders = json.loads(raw_orders) if raw_orders else {}
        page = int(request.GET.get("page", 1))

        mgr = DepartmentUserManager()
        records = mgr.get_list_page(
            params={
                "USER_ID": {
                    "type": "integer",
                    "filter": "EQUAL",
                    "values": current_user_id,
                }
            },
            order_by=orders,
            page=page,
            data_model=False,
        )

        return JsonResponse(records, status=200)
    except (TypeError, ValueError):
        return get_error_response("No se pudo identificar al usuario de sesion", status=401)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))

import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.managers.publication_manager import PublicationManager
from backend.models.publication_department_model import PublicationDepartmentModel
from backend.models.publication_model import PublicationModel
from backend.models.publication_user_model import PublicationUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=PublicationManager,
    model_class=PublicationModel,
    template_prefix="publication",
    singular_name="Publicación",
    created_message="Publicación creada correctamente",
    updated_message="Publicación actualizada correctamente",
    deleted_message="Publicación eliminada correctamente",
    not_found_message="No se encontró la publicación solicitada",
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
        "entity_model": PublicationModel.config(),
        "entity_model_publication_user": json.dumps(PublicationUserModel.config()),
        "entity_model_publication_department": json.dumps(PublicationDepartmentModel.config()),
    }
    return render(request, "publication/form.html", context_page)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView

from backend.views.api_value.api_value_urls import app_name as api_value_app
from backend.views.auth_app.auth_app_urls import app_name as auth_app

from backend.views.app_user.app_user_urls import app_name as app_user_app
from backend.views.department.department_urls import app_name as department_app
from backend.views.department_user.department_user_urls import app_name as department_user_app
from backend.views.document.document_urls import app_name as document_app
from backend.views.document_department.document_department_urls import app_name as document_department_app
from backend.views.document_user.document_user_urls import app_name as document_user_app
from backend.views.permission.permission_urls import app_name as permission_app
from backend.views.permission_user.permission_user_urls import app_name as permission_user_app
from backend.views.publication.publication_urls import app_name as publication_app
from backend.views.publication_department.publication_department_urls import app_name as publication_department_app
from backend.views.publication_user.publication_user_urls import app_name as publication_user_app
from backend.views.role.role_urls import app_name as role_app
from backend.views.role_permission.role_permission_urls import app_name as role_permission_app
from backend.views.role_user.role_user_urls import app_name as role_user_app


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: HttpResponse("ok", content_type="text/plain"), name="health"),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path(f"{auth_app}/", include(f"app.backend.views.{auth_app}.{auth_app}_urls")),
    path(f"{api_value_app}/", include(f"app.backend.views.{api_value_app}.{api_value_app}_urls")),

    path(f"{app_user_app}/", include(f"app.backend.views.{app_user_app}.{app_user_app}_urls")),
    path(f"{department_app}/", include(f"app.backend.views.{department_app}.{department_app}_urls")),
    path(f"{department_user_app}/", include(f"app.backend.views.{department_user_app}.{department_user_app}_urls")),
    path(f"{document_app}/", include(f"app.backend.views.{document_app}.{document_app}_urls")),
    path(f"{document_department_app}/", include(f"app.backend.views.{document_department_app}.{document_department_app}_urls")),
    path(f"{document_user_app}/", include(f"app.backend.views.{document_user_app}.{document_user_app}_urls")),
    path(f"{permission_app}/", include(f"app.backend.views.{permission_app}.{permission_app}_urls")),
    path(f"{permission_user_app}/", include(f"app.backend.views.{permission_user_app}.{permission_user_app}_urls")),
    path(f"{publication_app}/", include(f"app.backend.views.{publication_app}.{publication_app}_urls")),
    path(f"{publication_department_app}/", include(f"app.backend.views.{publication_department_app}.{publication_department_app}_urls")),
    path(f"{publication_user_app}/", include(f"app.backend.views.{publication_user_app}.{publication_user_app}_urls")),
    path(f"{role_app}/", include(f"app.backend.views.{role_app}.{role_app}_urls")),
    path(f"{role_permission_app}/", include(f"app.backend.views.{role_permission_app}.{role_permission_app}_urls")),
    path(f"{role_user_app}/", include(f"app.backend.views.{role_user_app}.{role_user_app}_urls")),
]

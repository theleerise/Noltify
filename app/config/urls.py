from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from backend.views.department.department_urls import app_name as department_app
from backend.views.role.role_urls import app_name as role_app


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path(f"{department_app}/", include(f"app.backend.views.{department_app}.{department_app}_urls")),
    path(f"{role_app}/", include(f"app.backend.views.{role_app}.{role_app}_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

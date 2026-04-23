"""
Configuración de rutas para role permission.

Este módulo define las URLs que exponen las vistas asociadas al contexto correspondiente dentro de la aplicación.
"""

from django.urls import path
from app.backend.views.role_permission import role_permission_views

app_name = "role_permission"

urlpatterns = [
    path("list/", role_permission_views.list_view, name="list"),
    path("data/", role_permission_views.data, name="data"),
    path("form/", role_permission_views.form_view, name="form"),
    path("new/", role_permission_views.new_view, name="new"),
    path("edit/<int:id>/", role_permission_views.edit_view, name="edit"),
    path("create/", role_permission_views.create, name="create"),
    path("update/<int:id>/", role_permission_views.update, name="update"),
    path("delete/<int:id>/", role_permission_views.delete, name="delete"),
]

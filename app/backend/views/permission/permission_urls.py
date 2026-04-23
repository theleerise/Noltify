"""
Configuración de rutas para permission.

Este módulo define las URLs que exponen las vistas asociadas al contexto correspondiente dentro de la aplicación.
"""

from django.urls import path
from app.backend.views.permission import permission_views

app_name = "permission"

urlpatterns = [
    path("list/", permission_views.list_view, name="list"),
    path("data/", permission_views.data, name="data"),
    path("form/", permission_views.form_view, name="form"),
    path("new/", permission_views.new_view, name="new"),
    path("edit/<int:id>/", permission_views.edit_view, name="edit"),
    path("create/", permission_views.create, name="create"),
    path("update/<int:id>/", permission_views.update, name="update"),
    path("delete/<int:id>/", permission_views.delete, name="delete"),
]

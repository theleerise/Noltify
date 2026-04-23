"""
Configuración de rutas para publication user.

Este módulo define las URLs que exponen las vistas asociadas al contexto correspondiente dentro de la aplicación.
"""

from django.urls import path
from app.backend.views.publication_user import publication_user_views

app_name = "publication_user"

urlpatterns = [
    path("list/", publication_user_views.list_view, name="list"),
    path("data/", publication_user_views.data, name="data"),
    path("form/", publication_user_views.form_view, name="form"),
    path("new/", publication_user_views.new_view, name="new"),
    path("edit/<int:id>/", publication_user_views.edit_view, name="edit"),
    path("create/", publication_user_views.create, name="create"),
    path("update/<int:id>/", publication_user_views.update, name="update"),
    path("delete/<int:id>/", publication_user_views.delete, name="delete"),
]

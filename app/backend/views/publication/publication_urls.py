"""
Configuración de rutas para publication.

Este módulo define las URLs que exponen las vistas asociadas al contexto correspondiente dentro de la aplicación.
"""

from django.urls import path
from app.backend.views.publication import publication_views

app_name = "publication"

urlpatterns = [
    path("list/", publication_views.list_view, name="list"),
    path("general/", publication_views.general_view, name="general"),
    path("general/data/", publication_views.general_data, name="general_data"),
    path("data/", publication_views.data, name="data"),
    path("form/", publication_views.form_view, name="form"),
    path("new/", publication_views.new_view, name="new"),
    path("edit/<int:id>/", publication_views.edit_view, name="edit"),
    path("general/create/", publication_views.general_create, name="general_create"),
    path("general/update/<int:id>/", publication_views.general_update, name="general_update"),
    path("general/delete/<int:id>/", publication_views.general_delete, name="general_delete"),
    path("create/", publication_views.create, name="create"),
    path("update/<int:id>/", publication_views.update, name="update"),
    path("delete/<int:id>/", publication_views.delete, name="delete"),
]

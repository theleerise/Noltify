from django.urls import path
from app.backend.views.publication import publication_views

app_name = "publication"

urlpatterns = [
    path("list/", publication_views.list_view, name="list"),
    path("data/", publication_views.data, name="data"),
    path("form/", publication_views.form_view, name="form"),
    path("new/", publication_views.new_view, name="new"),
    path("edit/<int:id>/", publication_views.edit_view, name="edit"),
    path("create/", publication_views.create, name="create"),
    path("update/<int:id>/", publication_views.update, name="update"),
    path("delete/<int:id>/", publication_views.delete, name="delete"),
]

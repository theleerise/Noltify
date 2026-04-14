from django.urls import path
from app.backend.views.publication_department import publication_department_views

app_name = "publication_department"

urlpatterns = [
    path("list/", publication_department_views.list_view, name="list"),
    path("data/", publication_department_views.data, name="data"),
    path("form/", publication_department_views.form_view, name="form"),
    path("new/", publication_department_views.new_view, name="new"),
    path("edit/<int:id>/", publication_department_views.edit_view, name="edit"),
    path("create/", publication_department_views.create, name="create"),
    path("update/<int:id>/", publication_department_views.update, name="update"),
    path("delete/<int:id>/", publication_department_views.delete, name="delete"),
]

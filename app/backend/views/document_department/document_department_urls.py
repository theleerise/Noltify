from django.urls import path
from app.backend.views.document_department import document_department_views

app_name = "document_department"

urlpatterns = [
    path("list/", document_department_views.list_view, name="list"),
    path("data/", document_department_views.data, name="data"),
    path("form/", document_department_views.form_view, name="form"),
    path("new/", document_department_views.new_view, name="new"),
    path("edit/<int:id>/", document_department_views.edit_view, name="edit"),
    path("create/", document_department_views.create, name="create"),
    path("update/<int:id>/", document_department_views.update, name="update"),
    path("delete/<int:id>/", document_department_views.delete, name="delete"),
]

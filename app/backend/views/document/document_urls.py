from django.urls import path
from app.backend.views.document import document_views

app_name = "document"

urlpatterns = [
    path("list/", document_views.list_view, name="list"),
    path("general/", document_views.general_view, name="general"),
    path("general/data/", document_views.general_data, name="general_data"),
    path("data/", document_views.data, name="data"),
    path("form/", document_views.form_view, name="form"),
    path("new/", document_views.new_view, name="new"),
    path("edit/<int:id>/", document_views.edit_view, name="edit"),
    path("file/<int:id>/", document_views.document_file, name="file"),
    path("general/create/", document_views.general_create, name="general_create"),
    path("general/update/<int:id>/", document_views.general_update, name="general_update"),
    path("general/delete/<int:id>/", document_views.general_delete, name="general_delete"),
    path("create/", document_views.create, name="create"),
    path("update/<int:id>/", document_views.update, name="update"),
    path("delete/<int:id>/", document_views.delete, name="delete"),
]

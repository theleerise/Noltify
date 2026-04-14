from django.urls import path
from app.backend.views.document import document_views

app_name = "document"

urlpatterns = [
    path("list/", document_views.list_view, name="list"),
    path("data/", document_views.data, name="data"),
    path("form/", document_views.form_view, name="form"),
    path("new/", document_views.new_view, name="new"),
    path("edit/<int:id>/", document_views.edit_view, name="edit"),
    path("create/", document_views.create, name="create"),
    path("update/<int:id>/", document_views.update, name="update"),
    path("delete/<int:id>/", document_views.delete, name="delete"),
]

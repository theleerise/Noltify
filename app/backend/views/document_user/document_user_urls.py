from django.urls import path
from app.backend.views.document_user import document_user_views

app_name = "document_user"

urlpatterns = [
    path("list/", document_user_views.list_view, name="list"),
    path("data/", document_user_views.data, name="data"),
    path("form/", document_user_views.form_view, name="form"),
    path("new/", document_user_views.new_view, name="new"),
    path("edit/<int:id>/", document_user_views.edit_view, name="edit"),
    path("create/", document_user_views.create, name="create"),
    path("update/<int:id>/", document_user_views.update, name="update"),
    path("delete/<int:id>/", document_user_views.delete, name="delete"),
]

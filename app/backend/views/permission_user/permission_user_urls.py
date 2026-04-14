from django.urls import path
from app.backend.views.permission_user import permission_user_views

app_name = "permission_user"

urlpatterns = [
    path("list/", permission_user_views.list_view, name="list"),
    path("data/", permission_user_views.data, name="data"),
    path("form/", permission_user_views.form_view, name="form"),
    path("new/", permission_user_views.new_view, name="new"),
    path("edit/<int:id>/", permission_user_views.edit_view, name="edit"),
    path("create/", permission_user_views.create, name="create"),
    path("update/<int:id>/", permission_user_views.update, name="update"),
    path("delete/<int:id>/", permission_user_views.delete, name="delete"),
]

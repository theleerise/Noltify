from django.urls import path
from app.backend.views.role_user import role_user_views

app_name = "role_user"

urlpatterns = [
    path("list/", role_user_views.list_view, name="list"),
    path("data/", role_user_views.data, name="data"),
    path("form/", role_user_views.form_view, name="form"),
    path("new/", role_user_views.new_view, name="new"),
    path("edit/<int:id>/", role_user_views.edit_view, name="edit"),
    path("create/", role_user_views.create, name="create"),
    path("update/<int:id>/", role_user_views.update, name="update"),
    path("delete/<int:id>/", role_user_views.delete, name="delete"),
]

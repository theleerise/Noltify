from django.urls import path
from app.backend.views.app_user import app_user_views

app_name = "app_user"

urlpatterns = [
    path("list/", app_user_views.list_view, name="list"),
    path("profile/", app_user_views.profile_view, name="profile"),
    path("data/", app_user_views.data, name="data"),
    path("form/", app_user_views.form_view, name="form"),
    path("new/", app_user_views.new_view, name="new"),
    path("edit/<int:id>/", app_user_views.edit_view, name="edit"),
    path("create/", app_user_views.create, name="create"),
    path("update/<int:id>/", app_user_views.update, name="update"),
    path("delete/<int:id>/", app_user_views.delete, name="delete"),
]

from django.urls import path
from app.backend.views.department_user import department_user_views

app_name = "department_user"

urlpatterns = [
    path("list/", department_user_views.list_view, name="list"),
    path("data/", department_user_views.data, name="data"),
    path("profile/data/", department_user_views.profile_data, name="profile_data"),
    path("form/", department_user_views.form_view, name="form"),
    path("new/", department_user_views.new_view, name="new"),
    path("edit/<int:id>/", department_user_views.edit_view, name="edit"),
    path("create/", department_user_views.create, name="create"),
    path("update/<int:id>/", department_user_views.update, name="update"),
    path("delete/<int:id>/", department_user_views.delete, name="delete"),
]

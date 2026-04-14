from django.urls import path
from app.backend.views.role import role_views

app_name = "role"

urlpatterns = [
    path("list/", role_views.list_view, name="list"),
    path("data/", role_views.data, name="data"),
    path("form/", role_views.form_view, name="form"),
    path("new/", role_views.new_view, name="new"),
    path("edit/<int:id>/", role_views.edit_view, name="edit"),
    path("create/", role_views.create, name="create"),
    path("update/<int:id>/", role_views.update, name="update"),
    path("delete/<int:id>/", role_views.delete, name="delete"),
]

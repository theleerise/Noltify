from django.urls import path
from app.backend.views.department import department_views

app_name = "department"

urlpatterns = [
    path("list/", department_views.list_view, name="list"),
    path("data/", department_views.data, name="data"),
    path("form/", department_views.form_view, name="form"),
    path("new/", department_views.new_view, name="new"),
    path("edit/<int:id>/", department_views.edit_view, name="edit"),
    path("create/", department_views.create, name="create"),
    path("update/<int:id>/", department_views.update, name="update"),
    path("delete/<int:id>/", department_views.delete, name="delete"),
]

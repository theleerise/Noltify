from django.urls import path
from app.backend.views.department import department_views

app_name = "department"

urlpatterns = [
    path("list/", department_views.list_view, name="list"),
    path("data/", department_views.data, name="data"),
#    path("form/", department_views.form_view, name="form"),
#    path("new/", department_views.new_view, name="new"),
#    path("edit/", department_views.edit_view, name="edit"),
#    path("create/", department_views.create_view, name="create"),
#    path("update/", department_views.update_view, name="update"),
#    path("update/<str:id>/", department_views.update_view, name="update_with_id"),
#    path("delete/", department_views.delete_view, name="delete"),
#    path("delete/<str:id>/", department_views.delete_view, name="delete_with_id"),
]
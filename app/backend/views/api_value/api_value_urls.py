from django.urls import path
from app.backend.views.api_value import api_value_views

app_name = "api_value"

urlpatterns = [
    path("data/<str:master>", api_value_views.data, name="data"),
    path("data_page/<str:master>", api_value_views.data_page, name="data_page"),
]
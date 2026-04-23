"""
Configuración de rutas para auth app.

Este módulo define las URLs que exponen las vistas asociadas al contexto correspondiente dentro de la aplicación.
"""

from django.urls import path

from app.backend.views.auth_app import auth_app_views


app_name = "auth_app"


urlpatterns = [
    path("login/", auth_app_views.login_view, name="login"),
    path("logout/", auth_app_views.logout_view, name="logout"),
]

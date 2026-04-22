"""
Middleware de autenticación de la aplicación.

Este middleware sincroniza el usuario guardado en sesión con el objeto
`request`, restringe el acceso a rutas privadas y gestiona redirecciones
automáticas hacia login o hacia la página principal cuando corresponde.
"""

from django.http import HttpResponseRedirect
from django.urls import reverse

from backend.core.auth_session import get_session_user


class AuthAppMiddleware:
    """
    Middleware encargado de validar el acceso básico a las rutas de la aplicación.

    Se aplica a cada petición HTTP y decide si el usuario puede continuar con
    el flujo normal o si debe ser redirigido al inicio de sesión.
    """

    PUBLIC_PREFIXES = (
        "/admin/",
        "/health/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        """
        Inicializa el middleware con la función siguiente de la cadena.

        Args:
            get_response: Callable que representa el siguiente middleware o la
                vista final que procesará la petición.

        Returns:
            None: El método únicamente deja configurada la instancia.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa cada petición entrante y aplica reglas básicas de autenticación.

        Este método carga el usuario desde sesión, determina si la ruta actual
        es pública o privada, y ejecuta las redirecciones necesarias cuando el
        usuario no está autenticado o intenta acceder al login estando ya
        autenticado.

        Args:
            request: Objeto request actual de Django.

        Returns:
            _type_: Respuesta HTTP generada por el middleware o por la vista
            siguiente en la cadena de ejecución.
        """
        request.app_user = get_session_user(request)

        login_url = reverse("auth_app:login")
        logout_url = reverse("auth_app:logout")
        current_path = request.path

        is_public_path = (
            current_path == login_url
            or current_path == logout_url
            or current_path == "/favicon.ico"
            or current_path.startswith(self.PUBLIC_PREFIXES)
        )

        is_authenticated = bool(request.app_user and request.app_user.get("id"))

        if not is_authenticated and not is_public_path:
            redirect_response = HttpResponseRedirect(f"{login_url}?next={request.get_full_path()}")
            return redirect_response

        if is_authenticated and current_path == login_url:
            return HttpResponseRedirect(reverse("home"))

        return self.get_response(request)

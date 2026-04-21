import json
from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from backend.core.auth_session import login_app_user, logout_app_user
from backend.core.authorization import require_any_permission, require_app_session
from backend.core.response import get_error_response, get_request_json, get_success_response
from backend.managers.app_user_manager import AppUserManager
from backend.models.app_user_model import AppUserModel
from backend.models.deparment_user_model import DepartmentUserModel
from backend.models.document_model import DocumentModel
from backend.models.document_user_model import DocumentUserModel
from backend.models.permission_user_model import PermissionUserModel
from backend.models.publication_model import PublicationModel
from backend.models.publication_user_model import PublicationUserModel
from backend.models.role_user_model import RoleUserModel
from app.backend.core.entity_crud import build_crud_views


_views = build_crud_views(
    manager_class=AppUserManager,
    model_class=AppUserModel,
    template_prefix="app_user",
    singular_name="Usuario",
    created_message="Usuario creado correctamente",
    updated_message="Usuario actualizado correctamente",
    deleted_message="Usuario eliminado correctamente",
    not_found_message="No se encontro el usuario solicitado",
    permission_prefix="APP_USER",
)

list_view = _views["list_view"]
data = _views["data"]
new_view = _views["new_view"]
edit_view = _views["edit_view"]
delete = _views["delete"]


class _PasswordValidationUser:
    def __init__(self, username: str | None, email: str | None, first_name: str | None, last_name: str | None):
        self.username = username or ""
        self.email = email or ""
        self.first_name = first_name or ""
        self.last_name = last_name or ""


def _request_user_is_superuser(request) -> bool:
    session_user = getattr(request, "app_user", None) or {}
    return bool(session_user.get("is_superuser"))


def _normalize_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _build_app_user_entity_model(request) -> dict:
    entity_model = deepcopy(AppUserModel.config())
    if not _request_user_is_superuser(request) and "is_superuser" in entity_model:
        entity_model["is_superuser"]["hidden_form"] = True
    return entity_model


@require_http_methods(["GET"])
@require_any_permission("APP_USER_LIST", "APP_USER_INSERT", "APP_USER_UPDATE")
def form_view(request):
    context_page = {
        "entity_model": _build_app_user_entity_model(request),
        "entity_model_department_user": json.dumps(DepartmentUserModel.config()),
        "entity_model_role_user": json.dumps(RoleUserModel.config()),
        "entity_model_permission_user": json.dumps(PermissionUserModel.config()),
        "entity_model_document_user": json.dumps(DocumentUserModel.config()),
        "entity_model_publication_user": json.dumps(PublicationUserModel.config()),
    }
    return render(request, "app_user/form.html", context_page)


def _get_profile_user(request):
    session_user = getattr(request, "app_user", None) or {}
    if not session_user.get("id"):
        return None, None

    try:
        profile_user_id = int(session_user.get("id"))
    except ValueError:
        return None, None

    mgr = AppUserManager()
    profile_user = mgr.get_by_id(record_id=profile_user_id, data_model=False)
    return profile_user, profile_user_id


def _build_profile_form_data(profile_user: dict | None, overrides: dict | None = None) -> dict:
    base_data = {
        "username": (profile_user or {}).get("username") or "",
        "email": (profile_user or {}).get("email") or "",
        "first_name": (profile_user or {}).get("first_name") or "",
        "last_name": (profile_user or {}).get("last_name") or "",
        "current_password": "",
        "new_password": "",
        "confirm_password": "",
        "confirm_deactivate": "",
    }
    if overrides:
        base_data.update(overrides)
    return base_data


def _build_profile_context(request, *, form_data: dict | None = None, form_errors: dict | None = None):
    profile_user, profile_user_id = _get_profile_user(request)

    full_name = ""
    if profile_user:
        first_name = (profile_user.get("first_name") or "").strip()
        last_name = (profile_user.get("last_name") or "").strip()
        full_name = " ".join(part for part in [first_name, last_name] if part).strip()

    context_page = {
        "profile_user": profile_user,
        "profile_user_id": profile_user_id,
        "profile_user_full_name": full_name,
        "department_user_entity_model": json.dumps(DepartmentUserModel.config()),
        "publication_entity_model": json.dumps(PublicationModel.config()),
        "document_entity_model": json.dumps(DocumentModel.config()),
        "profile_form_data": _build_profile_form_data(profile_user, overrides=form_data),
        "profile_form_errors": form_errors or {},
    }
    return context_page


def _validate_superuser_assignment(request, data: dict, existing_user: dict | None = None):
    current_is_superuser = bool(existing_user.get("is_superuser", False)) if existing_user else False

    if existing_user and "is_superuser" not in data:
        data["is_superuser"] = current_is_superuser

    if _request_user_is_superuser(request):
        return None

    requested_is_superuser = _normalize_bool(
        data.get(
            "is_superuser",
            current_is_superuser,
        )
    )

    if requested_is_superuser != current_is_superuser:
        return get_error_response(
            "Solo los superusuarios pueden asignar o retirar el estado de superusuario.",
            status=403,
        )

    data["is_superuser"] = current_is_superuser
    return None


def _validate_profile_input(manager: AppUserManager, profile_user: dict, post_data) -> tuple[dict, dict]:
    profile_user_id = int(profile_user["id"])
    username = (post_data.get("username") or "").strip()
    email = (post_data.get("email") or "").strip()
    first_name = (post_data.get("first_name") or "").strip()
    last_name = (post_data.get("last_name") or "").strip()
    current_password = post_data.get("current_password") or ""
    new_password = post_data.get("new_password") or ""
    confirm_password = post_data.get("confirm_password") or ""

    form_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "current_password": current_password,
        "new_password": new_password,
        "confirm_password": confirm_password,
        "confirm_deactivate": "",
    }

    errors: dict[str, str] = {}

    if not username:
        errors["username"] = "Debes indicar un nombre de usuario."
    elif manager.get_by_username(username, exclude_id=profile_user_id):
        errors["username"] = "Ese nombre de usuario ya esta en uso."

    if not email:
        errors["email"] = "Debes indicar un email."
    elif manager.get_by_email(email, exclude_id=profile_user_id):
        errors["email"] = "Ese email ya esta en uso."

    wants_password_change = bool(new_password or confirm_password)

    if wants_password_change:
        if not current_password:
            errors["current_password"] = "Debes informar tu contrasena actual para cambiar la contrasena."
        elif not check_password(current_password, profile_user.get("password_hash") or ""):
            errors["current_password"] = "La contrasena actual no es correcta."

        if not new_password:
            errors["new_password"] = "Debes indicar la nueva contrasena."
        elif new_password != confirm_password:
            errors["confirm_password"] = "La confirmacion de contrasena no coincide."
        else:
            validation_user = _PasswordValidationUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            try:
                validate_password(new_password, user=validation_user)
            except ValidationError as error:
                errors["new_password"] = " ".join(error.messages)

    update_data = {
        "id": profile_user_id,
        "username": username,
        "email": email,
        "first_name": first_name or None,
        "last_name": last_name or None,
        "is_active": bool(profile_user.get("is_active", True)),
        "is_superuser": bool(profile_user.get("is_superuser", False)),
    }

    if wants_password_change and "new_password" not in errors and "confirm_password" not in errors and "current_password" not in errors:
        update_data["password_hash"] = new_password

    return update_data, {"form_data": form_data, "errors": errors}


@require_http_methods(["POST"])
@require_any_permission("APP_USER_INSERT")
def create(request):
    try:
        request_data = get_request_json(request)
        data = request_data.get("data", {})

        superuser_error = _validate_superuser_assignment(request, data)
        if superuser_error:
            return superuser_error

        model = AppUserModel(**data)

        mgr = AppUserManager()
        result = mgr.insert_query(model.to_insert_dict())

        return get_success_response(
            data=result,
            message="Usuario creado correctamente",
            status=201,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["PUT"])
@require_any_permission("APP_USER_UPDATE")
def update(request, id: int):
    try:
        request_data = get_request_json(request)
        data = request_data.get("data", {})

        mgr = AppUserManager()
        existing_user = mgr.get_by_id(record_id=id, data_model=False)
        if not existing_user:
            return get_error_response(error="No se encontro el usuario solicitado", status=404)

        superuser_error = _validate_superuser_assignment(request, data, existing_user=existing_user)
        if superuser_error:
            return superuser_error

        data["id"] = id
        model = AppUserModel(**data)
        result = mgr.update_query(model.to_update_dict(include_primary_key=True))

        return get_success_response(
            data=result,
            message="Usuario actualizado correctamente",
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return get_error_response(str(e))


@require_http_methods(["GET"])
@require_app_session
def profile_view(request):
    return render(request, "app_user/profile.html", _build_profile_context(request))


@require_http_methods(["POST"])
@require_app_session
def profile_update_view(request):
    manager = AppUserManager()
    profile_user, _ = _get_profile_user(request)

    if not profile_user:
        messages.error(request, "No se pudo cargar tu perfil.")
        return redirect("app_user:profile")

    update_data, validation = _validate_profile_input(manager, profile_user, request.POST)
    form_errors = validation["errors"]
    form_data = validation["form_data"]

    if form_errors:
        context_page = _build_profile_context(request, form_data=form_data, form_errors=form_errors)
        return render(request, "app_user/profile.html", context_page, status=400)

    manager.update_query(update_data)
    updated_user = manager.get_by_id(record_id=profile_user["id"], data_model=False)
    if updated_user:
        login_app_user(request, updated_user)

    messages.success(request, "Tu perfil se ha actualizado correctamente.")
    return redirect("app_user:profile")


@require_http_methods(["POST"])
@require_app_session
def profile_deactivate_view(request):
    manager = AppUserManager()
    profile_user, profile_user_id = _get_profile_user(request)

    if not profile_user or not profile_user_id:
        messages.error(request, "No se pudo cargar tu perfil.")
        return redirect("app_user:profile")

    confirm_deactivate = (request.POST.get("confirm_deactivate") or "").strip().upper()
    current_password = request.POST.get("current_password") or ""

    form_data = _build_profile_form_data(
        profile_user,
        overrides={
            "confirm_deactivate": request.POST.get("confirm_deactivate") or "",
            "current_password": current_password,
        },
    )
    form_errors: dict[str, str] = {}

    if confirm_deactivate != "DESACTIVAR":
        form_errors["confirm_deactivate"] = "Escribe DESACTIVAR para confirmar la baja."

    if not current_password:
        form_errors["current_password"] = "Debes informar tu contrasena actual para darte de baja."
    elif not check_password(current_password, profile_user.get("password_hash") or ""):
        form_errors["current_password"] = "La contrasena actual no es correcta."

    if form_errors:
        context_page = _build_profile_context(request, form_data=form_data, form_errors=form_errors)
        return render(request, "app_user/profile.html", context_page, status=400)

    manager.update_query(
        {
            "id": profile_user_id,
            "username": profile_user.get("username"),
            "email": profile_user.get("email"),
            "first_name": profile_user.get("first_name"),
            "last_name": profile_user.get("last_name"),
            "is_active": False,
            "is_superuser": bool(profile_user.get("is_superuser", False)),
        }
    )

    logout_app_user(request)
    request.session.cycle_key()
    messages.success(request, "Tu usuario se ha marcado como inactivo.")
    return redirect("auth_app:login")

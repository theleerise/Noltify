from datetime import datetime

from pydantic import Field

from app.backend.core.entity_model import EntityModel


class AppUserModel(EntityModel):

    id: int | None = Field(
        default=None,
        title="ID",
        description="Identificador unico del usuario",
        pk=True,
        readonly=True,
        master_key="APP_USERS",
        hidden_form=True,
    )

    username: str = Field(..., title="Usuario", description="Nombre de usuario unico del sistema")
    email: str = Field(..., title="Email", description="Correo electronico del usuario")
    password_hash: str | None = Field(
        default=None,
        title="Contraseña",
        description="Contraseña de acceso del usuario. En edicion, dejala vacia para conservar la actual.",
        input_type="password",
        required_on_create=True,
        autocomplete="new-password",
    )

    first_name: str | None = Field(default=None, title="Nombre", description="Nombre del usuario")
    last_name: str | None = Field(default=None, title="Apellidos", description="Apellidos del usuario")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el usuario esta activo")
    is_superuser: bool = Field(default=False, title="Superusuario", description="Indica si el usuario tiene permisos administrativos")

    created_at: datetime | None = Field(
        default=None,
        title="Fec. Creacion",
        description="Fecha de creacion del usuario",
        readonly=True,
        hidden_form=True,
    )
    updated_at: datetime | None = Field(
        default=None,
        title="Fec. Actualizacion",
        description="Fecha de ultima actualizacion del usuario",
        readonly=True,
        hidden_form=True,
    )

    class Config:
        table_name = "APP_USER"
        primary_key = "id"

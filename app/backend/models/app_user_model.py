from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class AppUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador único del usuario")

    username: str = Field(..., title="Usuario", description="Nombre de usuario único del sistema")
    email: str = Field(..., title="Email", description="Correo electrónico del usuario")
    password_hash: str = Field(..., title="Password Hash", description="Hash de la contraseña del usuario")

    first_name: str | None = Field(default=None, title="Nombre", description="Nombre del usuario")
    last_name: str | None = Field(default=None, title="Apellidos", description="Apellidos del usuario")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el usuario está activo")
    is_superuser: bool = Field(default=False, title="Superusuario", description="Indica si el usuario tiene permisos administrativos")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del usuario")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de última actualización del usuario")

    class Config:
        table_name = "APP_USER"
        primary_key = "id"

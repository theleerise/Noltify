from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PermissionUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    user_id: int = Field(..., title="Usuario", description="Identificador del usuario")
    permission_id: int = Field(..., title="Permiso", description="Identificador del permiso")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del permiso al usuario")

    class Config:
        table_name = "PERMISSION_USER"
        primary_key = "id"

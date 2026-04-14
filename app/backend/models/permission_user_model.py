from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PermissionUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    user_id: int = Field(..., title="Usuario", description="Identificador del usuario", master_key="APP_USERS")
    permission_id: int = Field(..., title="Permiso", description="Identificador del permiso", master_key="PERMISSIONS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del permiso al usuario", readonly=True, hidden_form=True)

    class Config:
        table_name = "PERMISSION_USER"
        primary_key = "id"

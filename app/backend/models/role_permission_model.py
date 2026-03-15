from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class RolePermissionModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    role_id: int = Field(..., title="Rol", description="Identificador del rol")
    permission_id: int = Field(..., title="Permiso", description="Identificador del permiso")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del permiso al rol")

    class Config:
        table_name = "ROLE_PERMISSION"
        primary_key = "id"

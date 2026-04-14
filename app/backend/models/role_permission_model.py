from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class RolePermissionModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    role_id: int = Field(..., title="Rol", description="Identificador del rol", master_key="ROLES")
    permission_id: int = Field(..., title="Permiso", description="Identificador del permiso", master_key="PERMISSIONS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del permiso al rol", readonly=True, hidden_form=True)

    class Config:
        table_name = "ROLE_PERMISSION"
        primary_key = "id"

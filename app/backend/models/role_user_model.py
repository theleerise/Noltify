from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class RoleUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    user_id: int = Field(..., title="Usuario", description="Identificador del usuario", master_key="APP_USERS")
    role_id: int = Field(..., title="Rol", description="Identificador del rol", master_key="ROLES")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del rol al usuario", readonly=True, hidden_form=True)

    class Config:
        table_name = "ROLE_USER"
        primary_key = "id"

from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DepartmentUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    department_id: int = Field(..., title="Departamento", description="Identificador del departamento", master_key="DEPARTMENTS")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario", master_key="APP_USERS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del usuario al departamento", readonly=True, hidden_form=True)

    class Config:
        table_name = "DEPARTMENT_USER"
        primary_key = "id"

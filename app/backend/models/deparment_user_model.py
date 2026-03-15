from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DepartmentUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    department_id: int = Field(..., title="Departamento", description="Identificador del departamento")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del usuario al departamento")

    class Config:
        table_name = "DEPARTMENT_USER"
        primary_key = "id"

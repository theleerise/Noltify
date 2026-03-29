from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel

class DepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador del departamento", pk=True)

    code: str = Field(..., title="Código", description="Código único del departamento", nullable=False)
    name: str = Field(..., title="Nombre", description="Nombre del departamento", nullable=False)
    description: str | None = Field(default=None, title="Descripción", description="Descripción del departamento")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el departamento está activo")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del departamento")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de actualización del departamento")

    class Config:
        table_name = "DEPARTMENT"
        primary_key = "id"

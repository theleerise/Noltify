from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel

class DepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador del departamento", pk=True, readonly=True)

    code: str = Field(..., title="Código", description="Código único del departamento", nullable=False, table={
        "td": {"className": "text-nowrap"},
        "th": {"className": "text-nowrap"}
    })
    name: str = Field(..., title="Nombre", description="Nombre del departamento", nullable=False)
    description: str | None = Field(default=None, title="Descripción", description="Descripción del departamento", widget="textarea", rows=5)

    is_active: bool = Field(
        default=True, 
        title="Activo", 
        description="Indica si el departamento está activo", 
        boolean_config= {
            "values": {"true": True, "false": False},
            "display": {"true": "Si", "false": "No"}
        }
    )

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del departamento", readonly=True)
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de actualización del departamento", readonly=True)

    class Config:
        table_name = "DEPARTMENT"
        primary_key = "id"

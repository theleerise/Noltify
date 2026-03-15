from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class RoleModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador único del rol")

    code: str = Field(..., title="Código", description="Código único del rol")
    name: str = Field(..., title="Nombre", description="Nombre del rol")
    description: str | None = Field(default=None, title="Descripción", description="Descripción del rol")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el rol está activo")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del rol")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de última actualización del rol")

    class Config:
        table_name = "ROLE"
        primary_key = "id"
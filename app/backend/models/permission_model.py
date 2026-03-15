from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PermissionModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador único del permiso")

    code: str = Field(..., title="Código", description="Código único del permiso")
    name: str = Field(..., title="Nombre", description="Nombre descriptivo del permiso")
    description: str | None = Field(default=None, title="Descripción", description="Descripción detallada del permiso")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el permiso está activo")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del permiso")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de última actualización del permiso")

    class Config:
        table_name = "PERMISSION"
        primary_key = "id"

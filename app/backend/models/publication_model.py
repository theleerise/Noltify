from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la publicación")

    title: str = Field(..., title="Título", description="Título de la publicación")
    content: str | None = Field(default=None, title="Contenido", description="Contenido de la publicación")

    status: str = Field(default="DRAFT", title="Estado", description="Estado de la publicación")

    created_by: int | None = Field(default=None, title="Creado por", description="Usuario que creó la publicación")

    is_active: bool = Field(default=True, title="Activo", description="Indica si la publicación está activa")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación de la publicación")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de actualización de la publicación")

    class Config:
        table_name = "PUBLICATION"
        primary_key = "id"

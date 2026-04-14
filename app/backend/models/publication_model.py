from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la publicación", pk=True, readonly=True, master_key="PUBLICATIONS", hidden_form=True)

    title: str = Field(..., title="Título", description="Título de la publicación")
    content: str | None = Field(
        default=None,
        title="Contenido",
        description="Contenido de la publicación",
        widget="rich_editor",
        rows=8,
        placeholder="Escriba el contenido de la publicación...",
        height="320px"
    )

    status: str = Field(default="DRAFT", title="Estado", description="Estado de la publicación")

    created_by: int | None = Field(default=None, title="Creado por", description="Usuario que creó la publicación", master_key="APP_USERS")

    is_active: bool = Field(default=True, title="Activo", description="Indica si la publicación está activa")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación de la publicación", readonly=True, hidden_form=True)
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de actualización de la publicación", readonly=True, hidden_form=True)

    class Config:
        table_name = "PUBLICATION"
        primary_key = "id"

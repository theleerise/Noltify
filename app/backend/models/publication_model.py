from datetime import datetime

from pydantic import Field

from app.backend.core.entity_model import EntityModel


class PublicationModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la publicacion", pk=True, readonly=True, master_key="PUBLICATIONS", hidden_form=True)

    title: str = Field(..., title="Titulo", description="Titulo de la publicacion")
    content: str | None = Field(
        default=None,
        title="Contenido",
        description="Contenido de la publicacion",
        widget="rich_editor",
        rows=8,
        placeholder="Escriba el contenido de la publicacion...",
        height="320px"
    )

    status: str = Field(
        default="DRAFT",
        title="Estado",
        description="Estado de la publicacion",
        master_key="PUBLICATIONS_STATUS"
    )

    created_by: int | None = Field(default=None, title="Creado por", description="Usuario que creo la publicacion", master_key="APP_USERS", hidden_form=True)

    is_active: bool = Field(default=True, title="Activo", description="Indica si la publicacion esta activa")

    created_at: datetime | None = Field(default=None, title="Fec. Creacion", description="Fecha de creacion de la publicacion", readonly=True, hidden_form=True)
    updated_at: datetime | None = Field(default=None, title="Fec. Actualizacion", description="Fecha de actualizacion de la publicacion", readonly=True, hidden_form=True)

    class Config:
        table_name = "PUBLICATION"
        primary_key = "id"

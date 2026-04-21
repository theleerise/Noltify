from datetime import datetime

from pydantic import Field

from app.backend.core.entity_model import EntityModel


class DocumentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador del documento", pk=True, readonly=True, master_key="DOCUMENTS", hidden_form=True)

    title: str = Field(..., title="Titulo", description="Titulo del documento")
    file_name: str | None = Field(default=None, title="Nombre Archivo", description="Nombre original del archivo", hidden_form=True)
    file_binary: bytes | None = Field(default=None, title="Archivo", description="Archivo", widget="file", create_only=True)

    mime_type: str | None = Field(default=None, title="Tipo MIME", description="Tipo MIME del archivo", hidden_form=True)
    file_size: int | None = Field(default=None, title="Tamano", description="Tamano del archivo en bytes", hidden_form=True)

    description: str | None = Field(default=None, title="Descripcion", description="Descripcion del documento", widget="textarea", rows=5)

    uploaded_by: int | None = Field(default=None, title="Subido por", description="Usuario que subio el documento", master_key="APP_USERS", hidden_form=True)

    is_active: bool = Field(default=True, title="Activo", description="Indica si el documento esta activo")

    created_at: datetime | None = Field(default=None, title="Fec. Creacion", description="Fecha de creacion del documento", readonly=True, hidden_form=True)
    updated_at: datetime | None = Field(default=None, title="Fec. Actualizacion", description="Fecha de actualizacion del documento", readonly=True, hidden_form=True)

    class Config:
        table_name = "DOCUMENT"
        primary_key = "id"

from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DocumentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador del documento")

    title: str = Field(..., title="Título", description="Título del documento")
    file_name: str = Field(..., title="Nombre Archivo", description="Nombre original del archivo")
    file_path: str = Field(..., title="Ruta Archivo", description="Ruta física donde se almacena el archivo")

    mime_type: str | None = Field(default=None, title="Tipo MIME", description="Tipo MIME del archivo")
    file_size: int | None = Field(default=None, title="Tamaño", description="Tamaño del archivo en bytes")

    description: str | None = Field(default=None, title="Descripción", description="Descripción del documento")

    uploaded_by: int | None = Field(default=None, title="Subido por", description="Usuario que subió el documento")

    is_active: bool = Field(default=True, title="Activo", description="Indica si el documento está activo")

    created_at: datetime | None = Field(default=None, title="Fec. Creación", description="Fecha de creación del documento")
    updated_at: datetime | None = Field(default=None, title="Fec. Actualización", description="Fecha de actualización del documento")

    class Config:
        table_name = "DOCUMENT"
        primary_key = "id"

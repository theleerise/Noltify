from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DocumentUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    document_id: int = Field(..., title="Documento", description="Identificador del documento")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del documento al usuario")

    class Config:
        table_name = "DOCUMENT_USER"
        primary_key = "id"

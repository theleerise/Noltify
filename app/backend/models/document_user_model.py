from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DocumentUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    document_id: int = Field(..., title="Documento", description="Identificador del documento", master_key="DOCUMENTS")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario", master_key="APP_USERS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del documento al usuario", readonly=True, hidden_form=True)

    class Config:
        table_name = "DOCUMENT_USER"
        primary_key = "id"

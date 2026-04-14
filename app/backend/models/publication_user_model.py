from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    publication_id: int = Field(..., title="Publicación", description="Identificador de la publicación", master_key="PUBLICATIONS")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario", master_key="APP_USERS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación de la publicación al usuario", readonly=True, hidden_form=True)

    class Config:
        table_name = "PUBLICATION_USER"
        primary_key = "id"

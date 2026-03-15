from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationUserModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    publication_id: int = Field(..., title="Publicación", description="Identificador de la publicación")
    user_id: int = Field(..., title="Usuario", description="Identificador del usuario")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación de la publicación al usuario")

    class Config:
        table_name = "PUBLICATION_USER"
        primary_key = "id"

from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationDepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    publication_id: int = Field(..., title="Publicación", description="Identificador de la publicación")
    department_id: int = Field(..., title="Departamento", description="Identificador del departamento")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación de la publicación al departamento")

    class Config:
        table_name = "PUBLICATION_DEPARTMENT"
        primary_key = "id"

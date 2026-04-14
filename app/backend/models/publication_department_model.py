from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class PublicationDepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    publication_id: int = Field(..., title="Publicación", description="Identificador de la publicación", master_key="PUBLICATIONS")
    department_id: int = Field(..., title="Departamento", description="Identificador del departamento", master_key="DEPARTMENTS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación de la publicación al departamento", readonly=True, hidden_form=True)

    class Config:
        table_name = "PUBLICATION_DEPARTMENT"
        primary_key = "id"

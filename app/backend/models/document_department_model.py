from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DocumentDepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación")

    document_id: int = Field(..., title="Documento", description="Identificador del documento")
    department_id: int = Field(..., title="Departamento", description="Identificador del departamento")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del documento al departamento")

    class Config:
        table_name = "DOCUMENT_DEPARTMENT"
        primary_key = "id"

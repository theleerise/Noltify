from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class DocumentDepartmentModel(EntityModel):

    id: int | None = Field(default=None, title="ID", description="Identificador de la asignación", pk=True, readonly=True, hidden_form=True)

    document_id: int = Field(..., title="Documento", description="Identificador del documento", master_key="DOCUMENTS")
    department_id: int = Field(..., title="Departamento", description="Identificador del departamento", master_key="DEPARTMENTS")

    assigned_at: datetime | None = Field(default=None, title="Fec. Asignación", description="Fecha de asignación del documento al departamento", readonly=True, hidden_form=True)

    class Config:
        table_name = "DOCUMENT_DEPARTMENT"
        primary_key = "id"

from pydantic import Field
from datetime import datetime
from app.backend.core.entity_model import EntityModel


class ApiValueModel(EntityModel):

    id_row: int = Field(title="ID", description="Identificador")
    display_value: str = Field( title="Descripción", description="Descripción")

    class Config:
        #table_name = "APIVALUE"
        primary_key = "ID_ROW"

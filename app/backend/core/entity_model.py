from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class EntityModel(BaseModel):
    """
    Modelo base para todas las entidades de la aplicación.

    Responsabilidades:
        - Validar datos de entrada con Pydantic.
        - Permitir poblar modelos desde diccionarios.
        - Facilitar la conversión a dict/JSON para views y managers.
        - Ofrecer utilidades comunes para inserción, actualización y filtros.

    Esta clase está pensada para ser heredada por los modelos concretos,
    por ejemplo: DepartmentModel, UserModel, RoleModel, etc.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    __primary_key__: ClassVar[str | None] = "id"
    __exclude_none_by_default__: ClassVar[bool] = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "EntityModel":
        """
        Crea una instancia del modelo a partir de un diccionario.
        """
        return cls(**(data or {}))

    @classmethod
    def from_list(cls, items: list[dict[str, Any]] | None) -> list["EntityModel"]:
        """
        Crea una lista de instancias del modelo a partir de una lista de diccionarios.
        """
        if not items:
            return []

        return [cls.from_dict(item) for item in items]

    def to_dict(
        self,
        *,
        exclude_none: bool | None = None,
        by_alias: bool = True,
    ) -> dict[str, Any]:
        """
        Convierte la entidad a diccionario.
        """
        if exclude_none is None:
            exclude_none = self.__exclude_none_by_default__

        return self.model_dump(
            exclude_none=exclude_none,
            by_alias=by_alias,
        )

    def to_json_dict(self) -> dict[str, Any]:
        """
        Convierte la entidad a un diccionario seguro para serialización JSON.
        """
        json_ready_data = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        return json_ready_data

    def get_primary_key_value(self) -> Any:
        """
        Devuelve el valor de la clave primaria configurada en la entidad.
        """
        if not self.__primary_key__:
            return None

        return getattr(self, self.__primary_key__, None)

    def has_primary_key_value(self) -> bool:
        """
        Indica si la entidad tiene valor en su clave primaria.
        """
        primary_key_value = self.get_primary_key_value()
        return primary_key_value is not None

    def to_insert_dict(self) -> dict[str, Any]:
        """
        Devuelve un diccionario pensado para operaciones de inserción.

        Por defecto excluye campos nulos para evitar enviar columnas vacías a la capa de persistencia.
        """
        return self.to_dict(exclude_none=True)

    def to_update_dict(self, *, include_primary_key: bool = False) -> dict[str, Any]:
        """
        Devuelve un diccionario pensado para operaciones de actualización.

        Por defecto excluye la clave primaria, porque normalmente no debe modificarse.
        """
        update_data = self.to_dict(exclude_none=True)

        if not include_primary_key and self.__primary_key__ in update_data:
            update_data.pop(self.__primary_key__, None)

        return update_data

    @classmethod
    def build_filter_dict(cls, data: dict[str, Any] | None) -> dict[str, Any]:
        """
        Normaliza un diccionario de filtros eliminando claves no válidas.

        Esta utilidad es útil para managers que construyen consultas dinámicas a partir
        de todos los campos posibles del modelo.
        """
        if not data:
            return {}

        valid_fields = set(cls.model_fields.keys())
        normalized_filters: dict[str, Any] = {}

        for field_name, field_value in data.items():
            if field_name in valid_fields:
                normalized_filters[field_name] = field_value

        return normalized_filters

    def merge(self, data: dict[str, Any] | None) -> "EntityModel":
        """
        Devuelve una nueva instancia mezclando los valores actuales con los indicados.
        """
        merged_data = self.to_dict(exclude_none=False)
        merged_data.update(data or {})
        return self.__class__(**merged_data)

    def update_from_dict(self, data: dict[str, Any] | None) -> None:
        """
        Actualiza la instancia actual campo a campo usando validación de Pydantic.
        """
        if not data:
            return

        for field_name, field_value in data.items():
            if field_name in self.model_fields:
                setattr(self, field_name, field_value)

    @staticmethod
    def serialize_value(value: Any) -> Any:
        """
        Normaliza valores problemáticos antes de devolverlos al frontend.
        """
        if isinstance(value, Decimal):
            return float(value)

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, BaseModel):
            return value.model_dump(mode="json", exclude_none=True)

        if isinstance(value, list):
            return [EntityModel.serialize_value(item) for item in value]

        if isinstance(value, tuple):
            return [EntityModel.serialize_value(item) for item in value]

        if isinstance(value, dict):
            return {
                key: EntityModel.serialize_value(item)
                for key, item in value.items()
            }

        return value

    @classmethod
    def serialize_record(cls, record: dict[str, Any] | None) -> dict[str, Any]:
        """
        Convierte un registro plano a un diccionario serializable.
        """
        if not record:
            return {}

        return {
            key: cls.serialize_value(value)
            for key, value in record.items()
        }

    @classmethod
    def serialize_records(cls, records: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        """
        Convierte múltiples registros a una estructura compatible con JSON.
        """
        if not records:
            return []

        return [cls.serialize_record(record) for record in records]

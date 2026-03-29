from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict
from pydantic.fields import PydanticUndefined


class EntityModel(BaseModel):
    """
    Modelo base para todas las entidades de la aplicación.

    Responsabilidades:
        - Validar datos de entrada con Pydantic.
        - Permitir poblar modelos desde diccionarios.
        - Facilitar la conversión a dict/JSON para views y managers.
        - Ofrecer utilidades comunes para inserción, actualización y filtros.
        - Exponer una configuración de campos consumible por el frontend.
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
        return self.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )

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

        Por defecto excluye campos nulos para evitar enviar columnas vacías
        a la capa de persistencia.
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

        Esta utilidad es útil para managers que construyen consultas dinámicas
        a partir de todos los campos posibles del modelo.
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

        if isinstance(value, Enum):
            return value.value

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

    @classmethod
    def config(cls) -> dict[str, dict[str, Any]]:
        """
        Devuelve la configuración de los campos del modelo en formato dict.

        La salida está pensada para frontend dinámico, formularios automáticos,
        tablas, filtros o validación adicional en cliente.

        Reglas principales:
            - required = False si el campo:
                * es PK
                * acepta None
                * tiene default
            - cualquier atributo extra definido en Field(...) se conserva
            - si existe ui={...}, se incluye como bloque anidado
        """
        result: dict[str, dict[str, Any]] = {}

        for field_name, field_info in cls.model_fields.items():

            extra_config = dict(field_info.json_schema_extra or {})

            is_primary_key = bool(extra_config.get("pk", False))
            is_nullable = cls._is_nullable(field_info.annotation)
            has_default = cls._has_default(field_info.default, field_info.default_factory)

            field_config: dict[str, Any] = {
                "type": cls._map_python_type(field_info.annotation),
                "title": field_info.title or cls._build_default_title(field_name),
                "description": field_info.description,
                "required": cls._calculate_required(
                    is_primary_key=is_primary_key,
                    is_nullable=is_nullable,
                    has_default=has_default,
                ),
            }

            if has_default and field_info.default is not PydanticUndefined:
                field_config["default"] = cls.serialize_value(field_info.default)

            if is_primary_key:
                field_config["pk"] = True

            for extra_key, extra_value in extra_config.items():
                if extra_key not in field_config:
                    field_config[extra_key] = extra_value

            result[field_name] = {
                key: cls.serialize_value(value)
                for key, value in field_config.items()
                if value is not None
            }

        return result

    @staticmethod
    def _calculate_required(
        *,
        is_primary_key: bool,
        is_nullable: bool,
        has_default: bool,
    ) -> bool:
        """
        Determina si un campo debe considerarse obligatorio para entrada.

        Regla:
            - PK -> no requerido
            - nullable -> no requerido
            - default definido -> no requerido
            - resto -> requerido
        """
        if is_primary_key:
            return False

        if is_nullable:
            return False

        if has_default:
            return False

        return True

    @staticmethod
    def _has_default(default: Any, default_factory: Any) -> bool:
        """
        Indica si el campo tiene un valor por defecto.
        """
        if default is not PydanticUndefined:
            return True

        if default_factory is not None:
            return True

        return False

    @staticmethod
    def _is_nullable(annotation: Any) -> bool:
        """
        Indica si la anotación acepta None.
        """
        origin = get_origin(annotation)

        if origin is Union:
            return type(None) in get_args(annotation)

        return False

    @staticmethod
    def _map_python_type(annotation: Any) -> str:
        """
        Traduce el tipo Python/Pydantic a un tipo genérico de configuración.
        """
        resolved_annotation = EntityModel._unwrap_optional(annotation)
        origin = get_origin(resolved_annotation)

        if origin in (list, tuple, set):
            return "array"

        if origin is dict:
            return "object"

        type_map = {
            int: "integer",
            float: "number",
            Decimal: "decimal",
            str: "string",
            bool: "boolean",
            datetime: "datetime",
            date: "date",
        }

        return type_map.get(resolved_annotation, "string")

    @staticmethod
    def _unwrap_optional(annotation: Any) -> Any:
        """
        Si la anotación es Optional[T] o T | None, devuelve T.
        """
        origin = get_origin(annotation)

        if origin is Union:
            valid_types = [item for item in get_args(annotation) if item is not type(None)]
            if len(valid_types) == 1:
                return valid_types[0]

        return annotation

    @staticmethod
    def _build_default_title(field_name: str) -> str:
        """
        Genera un título por defecto legible a partir del nombre del campo.
        """
        return field_name.replace("_", " ").strip().title()
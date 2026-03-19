from __future__ import annotations

from datetime import datetime
from typing import Any

def get_query_row_count(sql: str) -> str:
    query = f"""
        SELECT COUNT(*) AS ROWS
        FROM (
            {sql}
        ) AS COUNT_QUERY
    """
    return query

def get_query_paginator(sql: str) -> str:
    query = f"""
        SELECT *
        FROM (
            {sql}
        ) AS PAGINATED_QUERY
        LIMIT %(paginator_query_limit)s
        OFFSET %(paginator_query_offset)s
    """
    return query

class QueryBuilder:
    """Clase utilizada para construir consultas SQL Dinamicas

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    
    FILTER_EQUAL = "EQUAL"
    FILTER_NOT_EQUAL = "NOT_EQUAL"
    FILTER_LIKE_CONTAINS = "LIKE_CONTAINS"
    FILTER_LIKE_STARTS_WITH = "LIKE_STARTS_WITH"
    FILTER_LIKE_ENDS_WITH = "LIKE_ENDS_WITH"
    FILTER_GREATER_THAN = "GREATER_THAN"
    FILTER_GREATER_EQUAL = "GREATER_EQUAL"
    FILTER_LESS_THAN = "LESS_THAN"
    FILTER_LESS_EQUAL = "LESS_EQUAL"
    FILTER_BETWEEN = "BETWEEN"
    FILTER_IN = "IN"
    FILTER_NOT_IN = "NOT_IN"
    FILTER_IS_NULL = "IS_NULL"
    FILTER_IS_NOT_NULL = "IS_NOT_NULL"

    TYPE_STRING = "string"
    TYPE_INTEGER = "integer"
    TYPE_FLOAT = "float"
    TYPE_DATE = "date"
    TYPE_BOOLEAN = "boolean"

    def build(self, base_sql: str, filters: dict[str, dict[str, Any]] | None = None) -> tuple[str, dict[str, Any]]:
        filters = filters or {}

        sql_lines = [base_sql.strip()]
        query_params: dict[str, Any] = {}

        for column_name, filter_config in filters.items():
            if not isinstance(filter_config, dict):
                continue

            field_type = filter_config.get("type")
            filter_operator = filter_config.get("filter")
            filter_values = filter_config.get("values")

            if not filter_operator:
                continue

            sql_condition, condition_params = self._build_condition(
                column_name=column_name,
                field_type=field_type,
                filter_operator=filter_operator,
                filter_values=filter_values
            )

            if not sql_condition:
                continue

            sql_lines.append(f"AND {sql_condition}")
            query_params.update(condition_params)

        final_sql = "\n".join(sql_lines)

        return final_sql, query_params

    def _build_condition(
        self,
        column_name: str,
        field_type: str | None,
        filter_operator: str,
        filter_values: Any
    ) -> tuple[str | None, dict[str, Any]]:
        normalized_operator = str(filter_operator).upper()
        normalized_column = column_name.upper()
        normalized_param = column_name.lower()

        if normalized_operator == self.FILTER_IS_NULL:
            return f"{normalized_column} IS NULL", {}

        if normalized_operator == self.FILTER_IS_NOT_NULL:
            return f"{normalized_column} IS NOT NULL", {}

        if self._is_empty(filter_values):
            return None, {}

        if normalized_operator == self.FILTER_EQUAL:
            return (
                f"{normalized_column} = %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_NOT_EQUAL:
            return (
                f"{normalized_column} <> %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_LIKE_CONTAINS:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {normalized_param: f"%{self._convert_value(field_type, filter_values)}%"}
            )

        if normalized_operator == self.FILTER_LIKE_STARTS_WITH:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {normalized_param: f"{self._convert_value(field_type, filter_values)}%"}
            )

        if normalized_operator == self.FILTER_LIKE_ENDS_WITH:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {normalized_param: f"%{self._convert_value(field_type, filter_values)}"}
            )

        if normalized_operator == self.FILTER_GREATER_THAN:
            return (
                f"{normalized_column} > %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_GREATER_EQUAL:
            return (
                f"{normalized_column} >= %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_LESS_THAN:
            return (
                f"{normalized_column} < %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_LESS_EQUAL:
            return (
                f"{normalized_column} <= %({normalized_param})s",
                {normalized_param: self._convert_value(field_type, filter_values)}
            )

        if normalized_operator == self.FILTER_BETWEEN:
            if not isinstance(filter_values, (tuple, list)) or len(filter_values) != 2:
                raise ValueError(
                    f"El filtro BETWEEN para la columna '{column_name}' debe recibir exactamente 2 valores."
                )

            start_param = f"{normalized_param}_start"
            end_param = f"{normalized_param}_end"

            return (
                f"{normalized_column} BETWEEN %({start_param})s AND %({end_param})s",
                {
                    start_param: self._convert_value(field_type, filter_values[0]),
                    end_param: self._convert_value(field_type, filter_values[1]),
                }
            )

        if normalized_operator == self.FILTER_IN:
            return self._build_in_condition(
                column_name=normalized_column,
                param_name=normalized_param,
                field_type=field_type,
                filter_values=filter_values,
                is_not_in=False
            )

        if normalized_operator == self.FILTER_NOT_IN:
            return self._build_in_condition(
                column_name=normalized_column,
                param_name=normalized_param,
                field_type=field_type,
                filter_values=filter_values,
                is_not_in=True
            )

        raise ValueError(
            f"El filtro '{filter_operator}' no está soportado para la columna '{column_name}'."
        )

    def _build_in_condition(
        self,
        column_name: str,
        param_name: str,
        field_type: str | None,
        filter_values: Any,
        is_not_in: bool = False
    ) -> tuple[str | None, dict[str, Any]]:
        if not isinstance(filter_values, (tuple, list)) or len(filter_values) == 0:
            return None, {}

        sql_params: dict[str, Any] = {}
        sql_placeholders: list[str] = []

        for index, item_value in enumerate(filter_values):
            current_param_name = f"{param_name}_{index}"
            sql_placeholders.append(f"%({current_param_name})s")
            sql_params[current_param_name] = self._convert_value(field_type, item_value)

        operator = "NOT IN" if is_not_in else "IN"

        return (
            f"{column_name} {operator} ({', '.join(sql_placeholders)})",
            sql_params
        )

    def _convert_value(self, field_type: str | None, value: Any) -> Any:
        if value is None:
            return None

        if field_type is None:
            return value

        normalized_type = str(field_type).lower()

        if normalized_type == self.TYPE_STRING:
            return str(value)

        if normalized_type == self.TYPE_INTEGER:
            return int(value)

        if normalized_type == self.TYPE_FLOAT:
            return float(value)

        if normalized_type == self.TYPE_BOOLEAN:
            return self._convert_boolean(value)

        if normalized_type == self.TYPE_DATE:
            return self._convert_date(value)

        return value

    def _convert_boolean(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value

        normalized_value = str(value).strip().lower()

        if normalized_value in ("true", "1", "yes", "y", "si", "sí"):
            return True

        if normalized_value in ("false", "0", "no", "n"):
            return False

        raise ValueError(f"No se puede convertir el valor '{value}' a boolean.")

    def _convert_date(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            for current_format in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
            ):
                try:
                    return datetime.strptime(value, current_format)
                except ValueError:
                    continue

        raise ValueError(f"No se puede convertir el valor '{value}' a fecha.")

    def _is_empty(self, value: Any) -> bool:
        if value is None:
            return True

        if isinstance(value, str) and value.strip() == "":
            return True

        if isinstance(value, (list, tuple)) and len(value) == 0:
            return True

        return False
"""
Herramientas para construir filtros, ordenación y envoltorios SQL dinámicos.

Este módulo permite generar setencias auxiliares para conteo, paginación y
filtrado a partir de configuraciones enviadas desde el frontend.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def get_query_row_count(sql: str) -> str:
    """
    Construye una consulta que devuelve el número total de filas de otra consulta.

    Args:
        sql (str): Consulta base sobre la que se desea realizar el conteo.

    Returns:
        str: Sentencia SQL que envuelve la consulta original y devuelve el total
        de registros.
    """
    query = f"""
        SELECT COUNT(*) AS ROWS
        FROM (
            {sql}
        ) AS COUNT_QUERY
    """
    return query


def get_query_paginator(sql: str) -> str:
    """
    Construye una consulta paginada a partir de una consulta base.

    La consulta resultante incorpora los parámetros `LIMIT` y `OFFSET`
    necesarios para recuperar únicamente un subconjunto de filas.

    Args:
        sql (str): Consulta base que se desea paginar.

    Returns:
        str: Sentencia SQL envuelta y preparada para recibir los parámetros de
        paginación.
    """
    query = f"""
        SELECT *
        FROM (
            {sql}
        ) AS PAGINATED_QUERY
        LIMIT %(paginator_query_limit)s
        OFFSET %(paginator_query_offset)s
    """
    return query


def get_query_base_wrapper(sql: str) -> str:
    """
    Envuelve una consulta SQL para facilitar la adición de condiciones extra.

    Este método añade una capa externa con `WHERE 1=1`, lo que simplifica la
    concatenación posterior de filtros dinámicos.

    Args:
        sql (str): Consulta base que se desea envolver.

    Returns:
        str: Consulta SQL preparada para recibir condiciones adicionales.
    """
    query = f"""
        SELECT *
        FROM (
            {sql}
        ) WHERE 1=1
    """

    return query


class QueryBuilder:
    """
    Clase encargada de construir cláusulas SQL dinámicas de filtrado y ordenación.

    Su objetivo es transformar la configuración enviada desde el frontend en
    fragmentos SQL seguros y compatibles con los managers de la aplicación.
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

    ORDER_ASC = "ASC"
    ORDER_DESC = "DESC"

    TYPE_STRING = "string"
    TYPE_INTEGER = "integer"
    TYPE_FLOAT = "float"
    TYPE_DATE = "date"
    TYPE_BOOLEAN = "boolean"

    def build(self, base_sql: str, filters: dict[str, dict[str, Any]] | None = None) -> tuple[str, dict[str, Any]]:
        """
        Construye una consulta SQL con condiciones dinámicas de filtrado.

        Args:
            base_sql (str): Consulta SQL base sobre la que se añadirán los
                filtros.
            filters (dict[str, dict[str, Any]] | None): Configuración de filtros
                enviada por el cliente.

        Returns:
            tuple[str, dict[str, Any]]: Consulta final construida y diccionario
            de parámetros necesarios para ejecutarla.
        """
        filters = filters or {}

        sql_lines = [base_sql.strip()]
        query_params: dict[str, Any] = {}

        for column_name, filter_config in filters.items():
            if not isinstance(filter_config, dict):
                continue

            field_type = filter_config.get("type")
            filter_operator = filter_config.get("filter")
            filter_values = filter_config.get("values")
            boolean_config = filter_config.get("boolean_config")

            if not filter_operator:
                continue

            sql_condition, condition_params = self._build_condition(
                column_name=column_name,
                field_type=field_type,
                filter_operator=filter_operator,
                filter_values=filter_values,
                boolean_config=boolean_config
            )

            if not sql_condition:
                continue

            sql_lines.append(f"AND {sql_condition}")
            query_params.update(condition_params)

        final_sql = "\n".join(sql_lines)

        return final_sql, query_params

    def build_order(
        self,
        base_sql: str,
        order_by: dict[str, str] | None = None
    ) -> str:
        """
        Añade una cláusula `ORDER BY` válida a una consulta base.

        Args:
            base_sql (str): Consulta SQL sobre la que se aplicará el orden.
            order_by (dict[str, str] | None): Diccionario que relaciona cada
                columna con su dirección de ordenación.

        Returns:
            str: Consulta SQL final con la cláusula `ORDER BY` incorporada si
            corresponde.
        """
        order_by = order_by or {}

        sql_lines = [base_sql.strip()]
        order_clauses: list[str] = []

        for column_name, direction in order_by.items():
            if self._is_empty(column_name) or self._is_empty(direction):
                continue

            normalized_column = str(column_name).upper().strip()
            normalized_direction = str(direction).upper().strip()

            if normalized_direction not in (self.ORDER_ASC, self.ORDER_DESC):
                raise ValueError(
                    f"La dirección de orden '{direction}' no es válida para la columna '{column_name}'. "
                    f"Solo se permite ASC o DESC."
                )

            if not self._is_safe_sql_identifier(normalized_column):
                raise ValueError(
                    f"El nombre de columna '{column_name}' no es válido para ORDER BY."
                )

            order_clauses.append(f"{normalized_column} {normalized_direction}")

        if order_clauses:
            sql_lines.append(f"ORDER BY {', '.join(order_clauses)}")

        return "\n".join(sql_lines)

    def _build_condition(
        self,
        column_name: str,
        field_type: str | None,
        filter_operator: str,
        filter_values: Any,
        boolean_config: dict[str, Any] | None = None
    ) -> tuple[str | None, dict[str, Any]]:
        """
        Construye la condición SQL y sus parámetros para un filtro concreto.

        Args:
            column_name (str): Nombre de la columna a filtrar.
            field_type (str | None): Tipo lógico del campo enviado por el
                frontend.
            filter_operator (str): Operador de filtrado que debe aplicarse.
            filter_values (Any): Valor o valores asociados al filtro.
            boolean_config (dict[str, Any] | None): Configuración adicional para
                interpretar valores booleanos.

        Returns:
            tuple[str | None, dict[str, Any]]: Fragmento SQL de la condición y
            diccionario de parámetros asociados.
        """
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
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
            )

        if normalized_operator == self.FILTER_NOT_EQUAL:
            return (
                f"{normalized_column} <> %({normalized_param})s",
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
            )

        if normalized_operator == self.FILTER_LIKE_CONTAINS:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {
                    normalized_param: f"%{self._convert_value(field_type, filter_values, boolean_config=boolean_config)}%"
                }
            )

        if normalized_operator == self.FILTER_LIKE_STARTS_WITH:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {
                    normalized_param: f"{self._convert_value(field_type, filter_values, boolean_config=boolean_config)}%"
                }
            )

        if normalized_operator == self.FILTER_LIKE_ENDS_WITH:
            return (
                f"{normalized_column} LIKE %({normalized_param})s",
                {
                    normalized_param: f"%{self._convert_value(field_type, filter_values, boolean_config=boolean_config)}"
                }
            )

        if normalized_operator == self.FILTER_GREATER_THAN:
            return (
                f"{normalized_column} > %({normalized_param})s",
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
            )

        if normalized_operator == self.FILTER_GREATER_EQUAL:
            return (
                f"{normalized_column} >= %({normalized_param})s",
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
            )

        if normalized_operator == self.FILTER_LESS_THAN:
            return (
                f"{normalized_column} < %({normalized_param})s",
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
            )

        if normalized_operator == self.FILTER_LESS_EQUAL:
            return (
                f"{normalized_column} <= %({normalized_param})s",
                {
                    normalized_param: self._convert_value(
                        field_type,
                        filter_values,
                        boolean_config=boolean_config
                    )
                }
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
                    start_param: self._convert_value(
                        field_type,
                        filter_values[0],
                        boolean_config=boolean_config
                    ),
                    end_param: self._convert_value(
                        field_type,
                        filter_values[1],
                        boolean_config=boolean_config
                    ),
                }
            )

        if normalized_operator == self.FILTER_IN:
            return self._build_in_condition(
                column_name=normalized_column,
                param_name=normalized_param,
                field_type=field_type,
                filter_values=filter_values,
                is_not_in=False,
                boolean_config=boolean_config
            )

        if normalized_operator == self.FILTER_NOT_IN:
            return self._build_in_condition(
                column_name=normalized_column,
                param_name=normalized_param,
                field_type=field_type,
                filter_values=filter_values,
                is_not_in=True,
                boolean_config=boolean_config
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
        is_not_in: bool = False,
        boolean_config: dict[str, Any] | None = None
    ) -> tuple[str | None, dict[str, Any]]:
        """
        Construye una condición SQL de tipo `IN` o `NOT IN`.

        Args:
            column_name (str): Nombre normalizado de la columna.
            param_name (str): Prefijo que se utilizará para los parámetros.
            field_type (str | None): Tipo del campo que se está procesando.
            filter_values (Any): Colección de valores a incluir en la condición.
            is_not_in (bool): Indica si debe construirse `NOT IN` en lugar de
                `IN`.
            boolean_config (dict[str, Any] | None): Configuración auxiliar para
                conversión de booleanos.

        Returns:
            tuple[str | None, dict[str, Any]]: Condición SQL generada y
            parámetros asociados.
        """
        if not isinstance(filter_values, (tuple, list)) or len(filter_values) == 0:
            return None, {}

        sql_params: dict[str, Any] = {}
        sql_placeholders: list[str] = []

        for index, item_value in enumerate(filter_values):
            current_param_name = f"{param_name}_{index}"
            sql_placeholders.append(f"%({current_param_name})s")
            sql_params[current_param_name] = self._convert_value(
                field_type,
                item_value,
                boolean_config=boolean_config
            )

        operator = "NOT IN" if is_not_in else "IN"

        return (
            f"{column_name} {operator} ({', '.join(sql_placeholders)})",
            sql_params
        )

    def _convert_value(
        self,
        field_type: str | None,
        value: Any,
        boolean_config: dict[str, Any] | None = None
    ) -> Any:
        """
        Convierte un valor recibido al tipo esperado por el filtro.

        Args:
            field_type (str | None): Tipo lógico del campo.
            value (Any): Valor recibido desde el filtro.
            boolean_config (dict[str, Any] | None): Configuración auxiliar para
                valores booleanos.

        Returns:
            Any: Valor convertido al tipo adecuado para la consulta SQL.
        """
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
            return self._convert_boolean(
                value,
                boolean_config=boolean_config
            )

        if normalized_type == self.TYPE_DATE:
            return self._convert_date(value)

        return value

    def _convert_boolean(
        self,
        value: Any,
        boolean_config: dict[str, Any] | None = None
    ) -> Any:
        """
        Convierte un valor recibido a un booleano o al valor booleano configurado.

        Args:
            value (Any): Valor que se desea interpretar como booleano.
            boolean_config (dict[str, Any] | None): Configuración opcional para
                mapear valores verdaderos y falsos personalizados.

        Returns:
            Any: Valor booleano normalizado según la configuración disponible.
        """
        if boolean_config:
            normalized_config = self._normalize_boolean_config(boolean_config)

            if self._matches_boolean_true(value, normalized_config):
                return normalized_config["values"]["true"]

            if self._matches_boolean_false(value, normalized_config):
                return normalized_config["values"]["false"]

        if isinstance(value, bool):
            return value

        normalized_value = str(value).strip().lower()

        if normalized_value in ("true", "1", "yes", "y", "s", "si", "sí"):
            return True

        if normalized_value in ("false", "0", "no", "n"):
            return False

        raise ValueError(f"No se puede convertir el valor '{value}' a boolean.")

    def _matches_boolean_true(
        self,
        value: Any,
        boolean_config: dict[str, Any]
    ) -> bool:
        """
        Comprueba si un valor debe interpretarse como verdadero.

        Args:
            value (Any): Valor que se desea comprobar.
            boolean_config (dict[str, Any]): Configuración booleana normalizada.

        Returns:
            bool: `True` si el valor represeta el estado verdadero.
        """
        return (
            value is True
            or self._same_value(value, boolean_config["values"]["true"])
            or str(value).strip().lower() == "true"
        )

    def _matches_boolean_false(
        self,
        value: Any,
        boolean_config: dict[str, Any]
    ) -> bool:
        """
        Comprueba si un valor debe interpretarse como falso.

        Args:
            value (Any): Valor que se desea comprobar.
            boolean_config (dict[str, Any]): Configuración booleana normalizada.

        Returns:
            bool: `True` si el valor represeta el estado falso.
        """
        return (
            value is False
            or self._same_value(value, boolean_config["values"]["false"])
            or str(value).strip().lower() == "false"
        )

    def _normalize_boolean_config(
        self,
        boolean_config: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        Completa la configuración booleana con valores por defecto.

        Args:
            boolean_config (dict[str, Any] | None): Configuración recibida para
                interpretar valores booleanos.

        Returns:
            dict[str, Any]: Configuración booleana completa y normalizada.
        """
        boolean_config = boolean_config or {}

        values = boolean_config.get("values") or {}
        display = boolean_config.get("display") or {}

        return {
            "values": {
                "true": values.get("true", True),
                "false": values.get("false", False),
            },
            "display": {
                "true": display.get("true", "Sí"),
                "false": display.get("false", "No"),
            }
        }

    def _same_value(self, left_value: Any, right_value: Any) -> bool:
        """
        Compara dos valores utilizando igualdad directa y normalización textual.

        Args:
            left_value (Any): Valor izquierdo de la comparación.
            right_value (Any): Valor derecho de la comparación.

        Returns:
            bool: `True` si ambos valores pueden considerarse equivalentes.
        """
        if left_value == right_value:
            return True

        if left_value is None or right_value is None:
            return False

        return str(left_value).strip().lower() == str(right_value).strip().lower()

    def _convert_date(self, value: Any) -> datetime:
        """
        Convierte un valor recibido a un objeto `datetime`.

        Args:
            value (Any): Valor de fecha o texto que se desea convertir.

        Returns:
            datetime: Fecha convertida al formato interno esperado.
        """
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
        """
        Indica si un valor debe tratarse como vacío dentro del filtrado.

        Args:
            value (Any): Valor que se desea evaluar.

        Returns:
            bool: `True` si el valor debe considerarse vacío.
        """
        if value is None:
            return True

        if isinstance(value, str) and value.strip() == "":
            return True

        if isinstance(value, (list, tuple)) and len(value) == 0:
            return True

        return False

    def _is_safe_sql_identifier(self, value: str) -> bool:
        """
        Comprueba si un identificador SQL contiene únicamente caracteres seguros.

        Args:
            value (str): Nombre de columna o identificador que se desea validar.

        Returns:
            bool: `True` si el identificador solo contiene caracteres permitidos.
        """
        allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_."

        if not value:
            return False

        for current_char in value:
            if current_char not in allowed_chars:
                return False

        return True

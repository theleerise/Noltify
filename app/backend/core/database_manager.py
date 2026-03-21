from __future__ import annotations

from typing import Any
import time

from backend.core.database_connection import DatabaseConnection
from backend.core.sql_builder import QueryBuilder, get_query_row_count, get_query_paginator
from backend.core.entity_model import EntityModel


class DatabaseManager:
    
    def __init__(self, model: type[EntityModel] | None = None, primary_key: str = "id", rows_page = 20):

        self.model_class = model
        self.primary_key = primary_key
        self.rows_page = rows_page 
        
        self.query_builder = QueryBuilder()
    # =========================================================
    # QUERIES TO IMPLEMENT
    # =========================================================

    def _select_query(self) -> str:
        raise NotImplementedError("Debes implementar el método _select_query().")

    def _insert_query(self) -> str:
        raise NotImplementedError("Debes implementar el método _insert_query().")

    def _update_query(self) -> str:
        raise NotImplementedError("Debes implementar el método _update_query().")

    def _delete_query(self) -> str:
        raise NotImplementedError("Debes implementar el método _delete_query().")
    
    def _calculate_page(self, page: int) -> dict:
        if not isinstance(page, int):
            raise ValueError("El parámetro 'page' debe ser un entero.")

        if page < 1:
            raise ValueError("El número de página debe ser mayor o igual a 1.")

        limit = self.rows_page
        offset = (page - 1) * self.rows_page

        return {
            "limit": limit,
            "offset": offset
        }

    # =========================================================
    # BASIC EXECUTION
    # =========================================================

    def execute_query(self, sql: str, params: dict[str, Any] | None = None,) -> Any | None:
        """
        Ejecuta una sentencia SQL y devuelve el resultado.
        """
        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                record = cursor.fetchall()
        
        return record
        
    def execute_query_data(self, sql: str, params: dict[str, Any] | None = None,) -> None:
        """
        Ejecuta una sentencia SQL sin devolver resultado.
        """
        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                connection.commit()

    # =========================================================
    # FETCHALL
    # =========================================================

    def fetchall(self, sql: str | None = None, params: dict[str, Any] | None = None, data_model: bool = True):
        """
        Ejecuta una consulta y devuelve todos los registros.
        Si no se informa sql, se utiliza _select_query().
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                records = cursor.fetchall()

        return self.after_fetchall(records, data_model)

    def after_fetchall(self, records: list[dict[str, Any]], data_model: bool = True):
        """
        Hook posterior a fetchall.
        """
        if not data_model:
            return records
        if self.model_class is None:
            return records

        return self.model_class.from_list(records)

    # =========================================================
    # FETCHONE
    # =========================================================

    def fetchone(self, sql: str | None = None, params: dict[str, Any] | None = None, data_model: bool = True):
        """
        Ejecuta una consulta y devuelve un único registro.
        Si no se informa sql, se utiliza _select_query().
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                record = cursor.fetchone()

        return self.after_fetchone(record, data_model)

    def after_fetchone(self, record: dict[str, Any] | None, data_model: bool = True):
        """
        Hook posterior a fetchone.
        """
        if record is None:
            return None

        if not data_model:
            return record
        if self.model_class is None:
            return record

        return self.model_class.from_dict(record)

    # =========================================================
    # GET BY ID
    # =========================================================

    def get_by_id(self, record_id: Any, data_model: bool = True):
        """
        Recupera un registro por su clave primaria utilizando _select_query().
        La consulta definida en _select_query() debe ser compatible con:
            WHERE id = %(id)s
        o con el nombre definido en self.primary_key.
        """
        return self.fetchone(
            params={self.primary_key: record_id}, 
            data_model=data_model
        )

    def get_list(self, params: dict = None, data_model: bool = True) -> dict:
        """
        Recupera una lista de registros de base de datos con/sin filtrado, se
        basa en la consulta principal asignada al manager

        Args:
            params (dict): Diccionario que contiene el filtro configurado para ejecutar la consulta

        Returns:
            _type_: Lista de objetos o diccionario con los registro de la entidad
        """

        sql_base = self._select_query()
        response = {}
        result = []
        count_rows = None

        try:
            start_time = time.perf_counter()

            if params:
                query_filter, query_params = self.query_builder.build(sql_base, params)
                query_count = get_query_row_count(query_filter)

                count_rows = self.execute_query(query_count, query_params)
                result = self.fetchall(sql=query_filter, params=query_params, data_model=data_model)

            else:
                query_count = get_query_row_count(sql_base)
                count_rows = self.execute_query(query_count)
                result = self.fetchall(sql=sql_base, data_model=data_model)

            end_time = time.perf_counter()

            response = {
                "data": result,
                "rows": count_rows[0].get("rows"),
                "time": round(end_time - start_time, 6)
            }

            return response

        except Exception as e:
            print(e)
            raise e

    def get_list_page(self, params: dict = None, page: int = 1, data_model: bool = True) -> dict:
        """
        Recupera una lista de registros de base de datos con/sin filtrado, se
        basa en la consulta principal asignada al manager

        Args:
            params (dict): Diccionario que contiene el filtro configurado para ejecutar la consulta

        Returns:
            _type_: Lista de objetos o diccionario con los registro de la entidad
        """

        sql_base = self._select_query()
        query_params = {}

        try:
            start_time = time.perf_counter()

            if params:
                query_filter, query_params = self.query_builder.build(sql_base, params)
                query_count = get_query_row_count(query_filter)
                query_paginate = get_query_paginator(query_filter)

                count_rows = self.execute_query(query_count, query_params)

                pages = self._calculate_page(page)
                query_params["paginator_query_limit"] = pages.get("limit")
                query_params["paginator_query_offset"] = pages.get("offset")

                result = self.fetchall(sql=query_paginate, params=query_params, data_model=data_model)
            else:
                query_count = get_query_row_count(sql_base)
                
                count_rows = self.execute_query(query_count)
                query_paginate = get_query_paginator(sql_base)

                pages = self._calculate_page(page)
                query_params["paginator_query_limit"] = pages.get("limit")
                query_params["paginator_query_offset"] = pages.get("offset")

                result = self.fetchall(sql=query_paginate, params=query_params, data_model=data_model)

            end_time = time.perf_counter()

            response = {
                "data": result,
                "rows": count_rows[0].get("rows"),
                "page": page,
                "time": round(end_time - start_time, 6)
            }

            return response

        except Exception as e:
            print(e)
            raise e

    # =========================================================
    # INSERT
    # =========================================================

    def insert_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la sentencia definida en _insert_query().
        """
        final_data = self._before_insert(data)

        self.execute_query_data(
            sql=self._insert_query(),
            params=final_data,
        )

        self._after_insert(final_data)

    def _before_insert(self, data: dict[str, Any],) -> dict[str, Any]:
        return data

    def _after_insert(self, data: dict[str, Any],) -> None:
        pass

    # =========================================================
    # UPDATE
    # =========================================================

    def update_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la sentencia definida en _update_query().
        El diccionario data debe contener la clave primaria si la consulta la necesita.
        """
        final_data = self._before_update(data)

        self.execute_query_data(
            sql=self._update_query(),
            params=final_data,
        )

        self._after_update(final_data)

    def _before_update(self, data: dict[str, Any],) -> dict[str, Any]:
        return data

    def _after_update(self, data: dict[str, Any],) -> None:
        pass

    # =========================================================
    # DELETE
    # =========================================================

    def delete_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la sentencia definida en _delete_query().
        """
        final_data = self._before_delete(data)

        self.execute_query_data(
            sql=self._delete_query(),
            params=final_data,
        )

        self._after_delete(final_data)

    def _before_delete(self, data: dict[str, Any],) -> dict[str, Any]:
        return data

    def _after_delete(self, data: dict[str, Any],) -> None:
        pass
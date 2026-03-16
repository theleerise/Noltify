from __future__ import annotations

from typing import Any

from backend.core.database_connection import DatabaseConnection
from backend.core.entity_model import EntityModel


class DatabaseManager:

    model_class: type[EntityModel] | None = None
    primary_key: str = "id"

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

    # =========================================================
    # BASIC EXECUTION
    # =========================================================

    def execute_query(self, sql: str, params: dict[str, Any] | None = None,) -> None:
        """
        Ejecuta una sentencia SQL sin devolver resultado.
        """
        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params or {})
                connection.commit()

    # =========================================================
    # FETCHALL
    # =========================================================

    def fetchall(self, params: dict[str, Any] | None = None, sql: str | None = None,):
        """
        Ejecuta una consulta y devuelve todos los registros.
        Si no se informa sql, se utiliza _select_query().
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(final_sql, params or {})
                records = cursor.fetchall()

        return self.after_fetchall(records)

    def after_fetchall(self, records: list[dict[str, Any]],):
        """
        Hook posterior a fetchall.
        """
        if self.model_class is None:
            return records

        return self.model_class.from_list(records)

    # =========================================================
    # FETCHONE
    # =========================================================

    def fetchone(self, params: dict[str, Any] | None = None, sql: str | None = None,
    ):
        """
        Ejecuta una consulta y devuelve un único registro.
        Si no se informa sql, se utiliza _select_query().
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(final_sql, params or {})
                record = cursor.fetchone()

        return self.after_fetchone(record)

    def after_fetchone(self, record: dict[str, Any] | None,):
        """
        Hook posterior a fetchone.
        """
        if record is None:
            return None

        if self.model_class is None:
            return record

        return self.model_class.from_dict(record)

    # =========================================================
    # GET BY ID
    # =========================================================

    def get_by_id(self, record_id: Any,):
        """
        Recupera un registro por su clave primaria utilizando _select_query().
        La consulta definida en _select_query() debe ser compatible con:
            WHERE id = %(id)s
        o con el nombre definido en self.primary_key.
        """
        return self.fetchone(
            params={self.primary_key: record_id}
        )

    # =========================================================
    # INSERT
    # =========================================================

    def insert_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la sentencia definida en _insert_query().
        """
        final_data = self._before_insert(data)

        self.execute_query(
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

        self.execute_query(
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

        self.execute_query(
            sql=self._delete_query(),
            params=final_data,
        )

        self._after_delete(final_data)

    def _before_delete(self, data: dict[str, Any],) -> dict[str, Any]:
        return data

    def _after_delete(self, data: dict[str, Any],) -> None:
        pass
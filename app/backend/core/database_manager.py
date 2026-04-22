"""
Módulo base para la gestión de operaciones de acceso a datos.

Este archivo define la clase `DatabaseManager`, utilizada como punto de
partida para los managers concretos de cada entidad. Aquí se centraliza la
ejecución de consultas, la obtención de registros individuales o listados, la
paginación, y las operaciones de inserción, actualización y borrado.
"""

from __future__ import annotations

from typing import Any
import time

from backend.core.database_connection import DatabaseConnection
from backend.core.sql_builder import QueryBuilder, get_query_row_count, get_query_paginator, get_query_base_wrapper
from backend.core.entity_model import EntityModel


class DatabaseManager:
    """
    Clase base para construir managers de acceso a base de datos.

    Esta clase proporciona un conjunto de utilidades comunes para trabajar con
    entidades persistidas. Su responsabilidad es encapsular la lógica general
    de lectura, escritura y transformación de resultados, dejando a cada
    manager hijo la definición concreta de las consultas SQL.
    """

    def __init__(self, model: type[EntityModel] | None = None, primary_key: str = "id", rows_page=20):
        """
        Inicializa la configuración básica del manager.

        Args:
            model (type[EntityModel] | None): Clase de modelo que se utilizará
                para transformar los registros obtenidos desde base de datos en
                objetos de dominio. Si no se informa, los resultados se podrán
                devolver como diccionarios planos.
            primary_key (str): Nombre de la clave primaria utilizada por la
                entidad administrada por este manager.
            rows_page (int): Cantidad de registros que se devolverán por página
                en las operaciones paginadas.

        Returns:
            None: Este método únicamente configura la instancia del manager.
        """
        self.model_class = model
        self.primary_key = primary_key
        self.rows_page = rows_page

        self.query_builder = QueryBuilder()

    # =========================================================
    # QUERIES TO IMPLEMENT
    # =========================================================

    def _select_query(self) -> str:
        """
        Devuelve la consulta base de selección para la entidad.

        Este método debe ser implementado por las clases hijas. La consulta
        retornada servirá como origen para listados, búsquedas por id y
        procesos de paginación.

        Returns:
            str: Consulta SQL principal utilizada para recuperar registros.
        """
        raise NotImplementedError("Debes implementar el método _select_query().")

    def _insert_query(self) -> str:
        """
        Devuelve la consulta SQL utilizada para insertar registros.

        Este método debe ser implementado por las clases hijas para definir la
        sentencia de inserción correspondiente a la entidad.

        Returns:
            str: Consulta SQL de inserción.
        """
        raise NotImplementedError("Debes implementar el método _insert_query().")

    def _update_query(self) -> str:
        """
        Devuelve la consulta SQL utilizada para actualizar registros.

        Este método debe ser implementado por las clases hijas para definir la
        sentencia de actualización correspondiente a la entidad.

        Returns:
            str: Consulta SQL de actualización.
        """
        raise NotImplementedError("Debes implementar el método _update_query().")

    def _delete_query(self) -> str:
        """
        Devuelve la consulta SQL utilizada para eliminar registros.

        Este método debe ser implementado por las clases hijas para definir la
        sentencia de borrado correspondiente a la entidad.

        Returns:
            str: Consulta SQL de eliminación.
        """
        raise NotImplementedError("Debes implementar el método _delete_query().")

    def _calculate_page(self, page: int) -> dict:
        """
        Calcula los parámetros de paginación a partir de un número de página.

        A partir del número de página solicitado y de la configuración
        `rows_page`, este método genera los valores `limit` y `offset`
        necesarios para una consulta paginada.

        Args:
            page (int): Número de página solicitado. Debe ser un entero mayor o
                igual a 1.

        Returns:
            dict: Diccionario con las claves `limit` y `offset` que se usarán
            en la consulta SQL paginada.
        """
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
        Ejecuta una consulta SQL y devuelve todos los registros obtenidos.

        Este método está pensado para consultas que retornan información, como
        listados, contadores o búsquedas específicas.

        Args:
            sql (str): Sentencia SQL que se desea ejecutar.
            params (dict[str, Any] | None): Diccionario con los parámetros
                necesarios para interpolar la consulta de forma segura. Si no se
                informa, la consulta se ejecuta sin parámetros.

        Returns:
            Any | None: Lista de registros devueltos por la consulta, según el
            comportamiento del cursor configurado.
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
        Ejecuta una sentencia SQL que modifica datos y confirma la transacción.

        Este método se utiliza para operaciones de escritura como inserciones,
        actualizaciones o eliminaciones, cuando no se necesita recuperar un
        conjunto de resultados.

        Args:
            sql (str): Sentencia SQL que se desea ejecutar.
            params (dict[str, Any] | None): Parámetros de la consulta. Si no se
                informan, la sentencia se ejecuta sin valores adicionales.

        Returns:
            None: La operación se ejecuta sobre base de datos y realiza commit.
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
        Ejecuta una consulta y devuelve todos los registros resultantes.

        Si no se informa una consulta SQL explícita, se utilizará la consulta
        base definida por `_select_query()`. El resultado puede devolverse como
        lista de diccionarios o como lista de instancias del modelo asociado.

        Args:
            sql (str | None): Consulta SQL a ejecutar. Si no se informa, se usa
                la consulta principal del manager.
            params (dict[str, Any] | None): Parámetros que se aplicarán a la
                consulta SQL.
            data_model (bool): Indica si los resultados deben convertirse a
                instancias del modelo configurado o devolverse como registros
                planos.

        Returns:
            _type_: Lista de objetos del modelo o lista de diccionarios con los
            registros recuperados desde base de datos.
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(final_sql, params)
                else:
                    cursor.execute(final_sql)
                records = cursor.fetchall()

        return self.after_fetchall(records, data_model)

    def after_fetchall(self, records: list[dict[str, Any]], data_model: bool = True):
        """
        Procesa el resultado de `fetchall` antes de devolverlo al consumidor.

        Este método actúa como un punto de extensión para transformar la
        colección de registros obtenida. Si `data_model` es verdadero y existe
        un modelo asociado, los diccionarios se convierten en instancias del
        modelo de entidad.

        Args:
            records (list[dict[str, Any]]): Registros crudos obtenidos desde la
                base de datos.
            data_model (bool): Indica si los resultados deben mapearse al modelo
                configurado.

        Returns:
            _type_: Lista de registros planos o lista de instancias del modelo.
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

        Si no se informa una consulta SQL, se utilizará la consulta principal
        del manager. El resultado puede devolverse como diccionario o como una
        instancia del modelo asociado.

        Args:
            sql (str | None): Consulta SQL que se desea ejecutar.
            params (dict[str, Any] | None): Parámetros necesarios para la
                ejecución de la consulta.
            data_model (bool): Define si el resultado debe transformarse en una
                instancia del modelo asociado.

        Returns:
            _type_: Un diccionario, una instancia del modelo o `None` si no se
            encontró ningún registro.
        """
        final_sql = sql or self._select_query()

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(final_sql, params)
                else:
                    cursor.execute(final_sql)
                record = cursor.fetchone()

        return self.after_fetchone(record, data_model)

    def after_fetchone(self, record: dict[str, Any] | None, data_model: bool = True):
        """
        Procesa el resultado de `fetchone` antes de devolverlo.

        Este método permite centralizar la conversión de un registro individual
        a una instancia del modelo asociado cuando corresponda.

        Args:
            record (dict[str, Any] | None): Registro obtenido desde base de
                datos o `None` si la consulta no produjo resultados.
            data_model (bool): Indica si se debe transformar el registro al
                modelo configurado.

        Returns:
            _type_: Registro plano, instancia del modelo o `None`.
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

    def get_by_id(self, sql: str | None = None, record_id: Any = None, data_model: bool = True):
        """
        Recupera un registro por su clave primaria.

        Este método envuelve la consulta base del manager para añadir un filtro
        por el campo definido como clave primaria. Resulta útil cuando se
        necesita obtener una entidad concreta a partir de su identificador.

        Args:
            sql (str | None): Consulta SQL base sobre la cual se aplicará el
                filtro por identificador. Si no se informa, se utilizará
                `_select_query()`.
            record_id (Any): Valor del identificador que se desea buscar.
            data_model (bool): Indica si el resultado debe mapearse al modelo.

        Returns:
            _type_: Registro encontrado como diccionario, como modelo o `None`
            si no existe coincidencia.
        """
        sql_base = sql or self._select_query()
        sql_wrap = get_query_base_wrapper(sql_base)
        sql_filter = f"""
            {sql_wrap}
            AND {self.primary_key} = %({self.primary_key})s
        """

        return self.fetchone(
            sql=sql_filter,
            params={self.primary_key: record_id},
            data_model=data_model
        )

    def get_list(self, sql: str | None = None, params: dict | None = None, order_by: dict[str, str] | None = None, data_model: bool = True) -> dict:
        """
        Recupera una lista de registros de base de datos con o sin filtrado.

        Este método se basa en la consulta principal asignada al manager y
        permite aplicar filtros dinámicos, ordenación y medición del tiempo de
        ejecución. El resultado final incluye tanto los datos como el número
        total de registros obtenidos.

        Args:
            sql (str | None): Consulta SQL base que se utilizará para obtener
                los registros. Si no se informa, se usa `_select_query()`.
            params (dict | None): Diccionario que contiene el filtro configurado
                para ejecutar la consulta.
            order_by (dict[str, str] | None): Configuración de ordenación por
                columnas, por ejemplo `{"name": "ASC"}`.
            data_model (bool): Indica si los datos deben transformarse a objetos
                del modelo o devolverse como diccionarios.

        Returns:
            dict: Diccionario con la lista de registros en `data`, el total de
            filas en `rows` y el tiempo de ejecución en `time`.
        """
        sql_base = sql or self._select_query()
        response = {}
        result = []
        count_rows = None

        try:
            start_time = time.perf_counter()
            final_sql = sql_base
            query_params = {}

            if params:
                final_sql, query_params = self.query_builder.build(sql_base, params)

            if order_by:
                final_sql = self.query_builder.build_order(final_sql, order_by)

            query_count = get_query_row_count(final_sql)

            if query_params:
                count_rows = self.execute_query(query_count, query_params)
                result = self.fetchall(sql=final_sql, params=query_params, data_model=data_model)
            else:
                count_rows = self.execute_query(query_count)
                result = self.fetchall(sql=final_sql, data_model=data_model)

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

    def get_list_page(self, sql: str | None = None, params: dict | None = None, order_by: dict[str, str] | None = None, page: int = 1, data_model: bool = True) -> dict:
        """
        Recupera una lista paginada de registros de base de datos.

        Este método aplica filtros, ordenación y paginación sobre la consulta
        principal del manager. Además de los datos de la página solicitada,
        devuelve el número total de filas y el tiempo de ejecución.

        Args:
            sql (str | None): Consulta SQL base sobre la que se aplicará la
                paginación. Si no se informa, se usa `_select_query()`.
            params (dict | None): Diccionario con los filtros que deben
                aplicarse a la consulta.
            order_by (dict[str, str] | None): Configuración de ordenación por
                columnas.
            page (int): Número de página que se desea recuperar.
            data_model (bool): Indica si el resultado debe transformarse a
                instancias del modelo.

        Returns:
            dict: Diccionario con los datos de la página en `data`, el total de
            filas en `rows`, la página actual en `page` y el tiempo empleado en
            `time`.
        """
        sql_base = sql or self._select_query()
        query_params = {}

        try:
            start_time = time.perf_counter()
            final_sql = sql_base

            if params:
                final_sql, query_params = self.query_builder.build(sql_base, params)

            if order_by:
                final_sql = self.query_builder.build_order(final_sql, order_by)

            query_count = get_query_row_count(final_sql)
            query_paginate = get_query_paginator(final_sql)

            if query_params:
                count_rows = self.execute_query(query_count, query_params)
            else:
                count_rows = self.execute_query(query_count)

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
        Ejecuta la operación de inserción para la entidad.

        Antes de lanzar la consulta SQL, los datos pasan por el hook
        `_before_insert`. Tras la ejecución, se invoca `_after_insert`, lo que
        permite personalizar comportamientos previos o posteriores.

        Args:
            data (dict[str, Any]): Diccionario con la información necesaria para
                insertar un nuevo registro.

        Returns:
            None: La operación persiste los datos en base de datos.
        """
        final_data = self._before_insert(data)

        self.execute_query_data(
            sql=self._insert_query(),
            params=final_data,
        )

        self._after_insert(final_data)

    def _before_insert(self, data: dict[str, Any],) -> dict[str, Any]:
        """
        Hook ejecutado antes de lanzar una inserción.

        Este método puede ser sobreescrito por managers concretos para
        normalizar, completar o validar datos antes de persistirlos.

        Args:
            data (dict[str, Any]): Datos preparados para la inserción.

        Returns:
            dict[str, Any]: Diccionario final que será utilizado en la consulta
            de inserción.
        """
        return data

    def _after_insert(self, data: dict[str, Any],) -> None:
        """
        Hook ejecutado después de una inserción exitosa.

        Puede utilizarse para disparar procesos secundarios, bitácoras o
        actualizaciones complementarias tras guardar un registro.

        Args:
            data (dict[str, Any]): Datos finalmente utilizados en la inserción.

        Returns:
            None: El método actúa como extensión posterior a la operación.
        """
        pass

    # =========================================================
    # UPDATE
    # =========================================================

    def update_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la operación de actualización para la entidad.

        El diccionario recibido debe contener la información necesaria para
        identificar y modificar el registro correspondiente. Antes y después de
        la actualización se ejecutan hooks que permiten personalizar el flujo.

        Args:
            data (dict[str, Any]): Datos necesarios para actualizar un registro.
                Debe incluir la clave primaria cuando la consulta la requiera.

        Returns:
            None: La operación actualiza los datos en base de datos.
        """
        final_data = self._before_update(data)

        self.execute_query_data(
            sql=self._update_query(),
            params=final_data,
        )

        self._after_update(final_data)

    def _before_update(self, data: dict[str, Any],) -> dict[str, Any]:
        """
        Hook ejecutado antes de realizar una actualización.

        Permite adaptar el contenido recibido antes de ejecutar la sentencia
        SQL de actualización.

        Args:
            data (dict[str, Any]): Datos a utilizar en la actualización.

        Returns:
            dict[str, Any]: Diccionario final que se enviará a la consulta.
        """
        return data

    def _after_update(self, data: dict[str, Any],) -> None:
        """
        Hook ejecutado después de una actualización exitosa.

        Este punto de extensión puede utilizarse para acciones complementarias
        posteriores a la actualización del registro.

        Args:
            data (dict[str, Any]): Datos utilizados durante la actualización.

        Returns:
            None: El método no devuelve información.
        """
        pass

    # =========================================================
    # DELETE
    # =========================================================

    def delete_query(self, data: dict[str, Any],) -> None:
        """
        Ejecuta la operación de eliminación para la entidad.

        Antes de ejecutar la consulta de borrado se da la oportunidad de
        transformar los datos mediante `_before_delete`. Tras la operación, se
        invoca `_after_delete`.

        Args:
            data (dict[str, Any]): Datos necesarios para identificar el registro
                que debe eliminarse.

        Returns:
            None: La operación elimina el registro en base de datos.
        """
        final_data = self._before_delete(data)

        self.execute_query_data(
            sql=self._delete_query(),
            params=final_data,
        )

        self._after_delete(final_data)

    def _before_delete(self, data: dict[str, Any],) -> dict[str, Any]:
        """
        Hook ejecutado antes de realizar una eliminación.

        Permite modificar o validar los datos antes de ejecutar la consulta de
        borrado.

        Args:
            data (dict[str, Any]): Datos recibidos para la operación de borrado.

        Returns:
            dict[str, Any]: Diccionario final que se enviará a la consulta.
        """
        return data

    def _after_delete(self, data: dict[str, Any],) -> None:
        """
        Hook ejecutado después de una eliminación exitosa.

        Puede utilizarse para tareas complementarias que deban producirse
        después de borrar un registro.

        Args:
            data (dict[str, Any]): Datos utilizados durante la eliminación.

        Returns:
            None: El método no devuelve valores.
        """
        pass

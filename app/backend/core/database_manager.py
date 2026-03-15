from backend.core.database_connection import DatabaseConnection


class DatabaseManager:

    def execute_query(self, sql, params=None):
        """Ejecuta una sentencia para devolver un listado de registros de base de datos.

        Args:
            sql (str): sentencia SQL a ejecutar
            params (dict, optional): Diccionario con los parametros a utilizar dentro de la consulta. Defaults to None.

        Returns:
            list[dict]: Lista de diccionarios que contienen los registros de la consulta.
        """
        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.description:
                    return cursor.fetchall()
                return None
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from django.conf import settings


class DatabaseConnection:
    """
    Gestiona el pool de conexiones a PostgreSQL.
    """

    _pool: ConnectionPool | None = None


    @classmethod
    def initialize_pool(cls):

        if cls._pool is not None:
            return

        database = settings.DATABASES["default"]

        connection_string = (
            f"dbname={database['NAME']} "
            f"user={database['USER']} "
            f"password={database['PASSWORD']} "
            f"host={database['HOST']} "
            f"port={database['PORT']}"
        )

        cls._pool = ConnectionPool(
            connection_string,
            min_size=1,
            max_size=10,
            kwargs={
                "row_factory": dict_row
            }
        )


    @classmethod
    def get_connection(cls):
        """
        Devuelve una conexion a base de datos disponible dentro del pool de conexiones

        Returns:
            _type_: conexion a base de datos
        """
        if cls._pool is None:
            cls.initialize_pool()

        return cls._pool.connection()


    @classmethod
    def close_pool(cls):
        """
        Cierra el pool de conexiones de la aplicación
        """
        if cls._pool:
            cls._pool.close()
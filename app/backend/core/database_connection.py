"""
Gestión del pool de conexiones PostgreSQL de la aplicación.

Este módulo centraliza la creación, reutilización y cierre del pool de
conexiones utilizado por la capa de acceso a datos del proyecto.
"""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from django.conf import settings


class DatabaseConnection:
    """
    Clase encargada de administrar el pool compartido de conexiones a base de datos.

    Su objetivo es exponer una única configuración de pool para toda la
    aplicación, evitando crear conexiones independientes en cada operación.
    """

    _pool: ConnectionPool | None = None

    @classmethod
    def initialize_pool(cls):
        """
        Inicializa el pool de conexiones si todavía no ha sido creado.

        El método toma la configuración definida en Django y construye la
        cadena de conexión necesaria para crear el pool con `psycopg_pool`.

        Returns:
            None: El método deja inicializado el pool compartido de conexiones.
        """
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
            max_size=20,
            kwargs={
                "row_factory": dict_row
            }
        )

    @classmethod
    def get_connection(cls):
        """
        Obtiene una conexión disponible desde el pool compartido.

        Si el pool todavía no existe, lo inicializa automáticamente antes de
        devolver la conexión.

        Returns:
            _type_: Conexión activa obtenida desde el pool de la aplicación.
        """
        if cls._pool is None:
            cls.initialize_pool()

        return cls._pool.connection()

    @classmethod
    def close_pool(cls):
        """
        Cierra el pool de conexiones de la aplicación.

        Este método debe utilizarse cuando se necesite liberar explícitamente
        los recursos asociados al pool compartido.

        Returns:
            None: El pool queda cerrado si había sido inicializado previamente.
        """
        if cls._pool:
            cls._pool.close()

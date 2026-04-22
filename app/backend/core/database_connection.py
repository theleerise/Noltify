"""PostgreSQL connection-pool management for the backend data layer."""

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from django.conf import settings


class DatabaseConnection:
    """Manage the shared PostgreSQL connection pool for the application."""

    _pool: ConnectionPool | None = None

    @classmethod
    def initialize_pool(cls):
        """Initialize the shared psycopg connection pool only once."""
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
        """Return an available database connection from the shared pool."""
        if cls._pool is None:
            cls.initialize_pool()

        return cls._pool.connection()

    @classmethod
    def close_pool(cls):
        """Close the shared connection pool used by the application."""
        if cls._pool:
            cls._pool.close()

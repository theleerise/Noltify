"""
Manager de acceso a datos para role.

Este módulo concentra las consultas y operaciones de persistencia asociadas a la entidad o relación correspondiente.
"""

from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.role_model import RoleModel


class RoleManager(DatabaseManager):
    """
    Manager encargado de encapsular las operaciones de acceso a datos de la entidad asociada.

    Esta clase centraliza las consultas SQL, los ajustes previos a inserción o actualización y cualquier comportamiento adicional requerido por la entidad.
    """

    def __init__(self):
        """
        Inicializa el manager con la configuración base de la entidad.

        Returns:
            None: El método deja preparada la clase base con el modelo, la clave primaria y la configuración de paginación necesarias.
        """
        super().__init__(RoleModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , CODE
                , NAME
                , DESCRIPTION
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.ROLE
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.ROLE (
                  CODE
                , NAME
                , DESCRIPTION
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            ) VALUES (
                  %(code)s
                , %(name)s
                , %(description)s
                , %(is_active)s
                , %(created_at)s
                , %(updated_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.ROLE
            SET
                  CODE = %(code)s
                , NAME = %(name)s
                , DESCRIPTION = %(description)s
                , IS_ACTIVE = %(is_active)s
                , UPDATED_AT = %(updated_at)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.ROLE
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        """
        Ajusta los datos antes de insertar un rol.

        Args:
            data (dict): Información del rol que se desea persistir.

        Returns:
            dict: Diccionario final con las marcas temporales necesarias para la
            inserción.
        """
        return self._apply_timestamp_audit_on_insert(data)

    def _before_update(self, data: dict) -> dict:
        """
        Ajusta los datos antes de actualizar un rol existente.

        Args:
            data (dict): Datos recibidos para la actualización del rol.

        Returns:
            dict: Diccionario final preparado para la operación de actualización.
        """
        return self._apply_timestamp_audit_on_update(data)

    @staticmethod
    def _apply_timestamp_audit_on_insert(data: dict) -> dict:
        """
        Añade las fechas de creación y actualización a un rol nuevo.

        Args:
            data (dict): Datos del rol que se va a insertar.

        Returns:
            dict: Diccionario con las marcas temporales incorporadas.
        """
        now = datetime.now()
        data["created_at"] = now
        data["updated_at"] = now
        return data

    @staticmethod
    def _apply_timestamp_audit_on_update(data: dict) -> dict:
        """
        Actualiza la fecha de modificación de un rol.

        Args:
            data (dict): Datos del rol que se va a actualizar.

        Returns:
            dict: Diccionario con la fecha de actualización renovada.
        """
        data["updated_at"] = datetime.now()
        return data


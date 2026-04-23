"""
Manager de acceso a datos para permission user.

Este módulo concentra las consultas y operaciones de persistencia asociadas a la entidad o relación correspondiente.
"""

from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.permission_user_model import PermissionUserModel


class PermissionUserManager(DatabaseManager):
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
        super().__init__(PermissionUserModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , USER_ID
                , PERMISSION_ID
                , ASSIGNED_AT
            FROM PUBLIC.PERMISSION_USER
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.PERMISSION_USER (
                  USER_ID
                , PERMISSION_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(user_id)s
                , %(permission_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.PERMISSION_USER
            SET
                  USER_ID = %(user_id)s
                , PERMISSION_ID = %(permission_id)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.PERMISSION_USER
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        return self._apply_assignment_audit_on_insert(data)

    def _before_update(self, data: dict) -> dict:
        data.pop("assigned_at", None)
        return data

    @staticmethod
    def _apply_assignment_audit_on_insert(data: dict) -> dict:
        data["assigned_at"] = datetime.now()
        return data


"""
Manager de acceso a datos para department.

Este módulo concentra las consultas y operaciones de persistencia asociadas a la entidad o relación correspondiente.
"""

from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.department_model import DepartmentModel


class DepartmentManager(DatabaseManager):
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
        super().__init__(DepartmentModel, "id", rows_page=10)
        
    def _select_query(self) -> str:
        query = """
            SELECT
                  ID 
                , CODE
                , NAME
                , DESCRIPTION
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.DEPARTMENT
            WHERE 1 = 1
        """
        return query
        
    def _insert_query(self):
        query = """
            INSERT INTO PUBLIC.DEPARTMENT (
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
        return query
    
    def _update_query(self):
        query = """
            UPDATE PUBLIC.DEPARTMENT
            SET
                  CODE = %(code)s
                , NAME = %(name)s
                , DESCRIPTION = %(description)s
                , IS_ACTIVE = %(is_active)s
                , UPDATED_AT = %(updated_at)s
            WHERE ID = %(id)s
        """
        return query
    
    def _delete_query(self):
        query = """
            DELETE FROM PUBLIC.DEPARTMENT
            WHERE ID = %(id)s
        """
        return query
    
    def _before_update(self, data: dict) -> dict:
        return self._apply_timestamp_audit_on_update(data)
    
    def _before_insert(self, data: dict) -> dict:
        return self._apply_timestamp_audit_on_insert(data)

    @staticmethod
    def _apply_timestamp_audit_on_insert(data: dict) -> dict:
        now = datetime.now()
        data["created_at"] = now
        data["updated_at"] = now
        return data

    @staticmethod
    def _apply_timestamp_audit_on_update(data: dict) -> dict:
        data["updated_at"] = datetime.now()
        return data


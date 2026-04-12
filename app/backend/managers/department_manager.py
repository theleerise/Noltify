from backend.core.database_manager import DatabaseManager
from backend.models.department_model import DepartmentModel


class DepartmentManager(DatabaseManager):
    
    def __init__(self):
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
        
        
        
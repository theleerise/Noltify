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
        
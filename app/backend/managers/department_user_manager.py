from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.deparment_user_model import DepartmentUserModel


class DepartmentUserManager(DatabaseManager):

    def __init__(self):
        super().__init__(DepartmentUserModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  DEUS.ID
                , DEUS.DEPARTMENT_ID
				, DE.CODE AS DEPARTMENT_ID_DISPLAY
                , DEUS.USER_ID
				, CONCAT(US.USERNAME, ' (', US.FIRST_NAME, ' ', US.LAST_NAME, ')') AS USER_ID_DISPLAY
                , DEUS.ASSIGNED_AT
            FROM PUBLIC.DEPARTMENT_USER AS DEUS
			LEFT JOIN PUBLIC.DEPARTMENT AS DE
			    ON DE.ID = DEUS.DEPARTMENT_ID
			LEFT JOIN PUBLIC.APP_USER AS US
			    ON US.ID = DEUS.USER_ID
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.DEPARTMENT_USER (
                  DEPARTMENT_ID
                , USER_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(department_id)s
                , %(user_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.DEPARTMENT_USER
            SET
                  DEPARTMENT_ID = %(department_id)s
                , USER_ID = %(user_id)s
                , ASSIGNED_AT = %(assigned_at)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.DEPARTMENT_USER
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        data["assigned_at"] = datetime.now()
        return data

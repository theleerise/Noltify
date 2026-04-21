from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.role_user_model import RoleUserModel


class RoleUserManager(DatabaseManager):

    def __init__(self):
        super().__init__(RoleUserModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , USER_ID
                , ROLE_ID
                , ASSIGNED_AT
            FROM PUBLIC.ROLE_USER
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.ROLE_USER (
                  USER_ID
                , ROLE_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(user_id)s
                , %(role_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.ROLE_USER
            SET
                  USER_ID = %(user_id)s
                , ROLE_ID = %(role_id)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.ROLE_USER
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

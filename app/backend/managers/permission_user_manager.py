from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.permission_user_model import PermissionUserModel


class PermissionUserManager(DatabaseManager):

    def __init__(self):
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

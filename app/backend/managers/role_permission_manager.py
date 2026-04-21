from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.role_permission_model import RolePermissionModel


class RolePermissionManager(DatabaseManager):

    def __init__(self):
        super().__init__(RolePermissionModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , ROLE_ID
                , PERMISSION_ID
                , ASSIGNED_AT
            FROM PUBLIC.ROLE_PERMISSION
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.ROLE_PERMISSION (
                  ROLE_ID
                , PERMISSION_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(role_id)s
                , %(permission_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.ROLE_PERMISSION
            SET
                  ROLE_ID = %(role_id)s
                , PERMISSION_ID = %(permission_id)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.ROLE_PERMISSION
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

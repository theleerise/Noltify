from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.permission_model import PermissionModel


class PermissionManager(DatabaseManager):

    def __init__(self):
        super().__init__(PermissionModel, "id", rows_page=10)

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
            FROM PUBLIC.PERMISSION
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.PERMISSION (
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
            UPDATE PUBLIC.PERMISSION
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
            DELETE FROM PUBLIC.PERMISSION
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        return self._apply_timestamp_audit_on_insert(data)

    def _before_update(self, data: dict) -> dict:
        return self._apply_timestamp_audit_on_update(data)

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

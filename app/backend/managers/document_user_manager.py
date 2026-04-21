from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.document_user_model import DocumentUserModel


class DocumentUserManager(DatabaseManager):

    def __init__(self):
        super().__init__(DocumentUserModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , DOCUMENT_ID
                , USER_ID
                , ASSIGNED_AT
            FROM PUBLIC.DOCUMENT_USER
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.DOCUMENT_USER (
                  DOCUMENT_ID
                , USER_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(document_id)s
                , %(user_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.DOCUMENT_USER
            SET
                  DOCUMENT_ID = %(document_id)s
                , USER_ID = %(user_id)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.DOCUMENT_USER
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

from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.document_department_model import DocumentDepartmentModel


class DocumentDepartmentManager(DatabaseManager):

    def __init__(self):
        super().__init__(DocumentDepartmentModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , DOCUMENT_ID
                , DEPARTMENT_ID
                , ASSIGNED_AT
            FROM PUBLIC.DOCUMENT_DEPARTMENT
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.DOCUMENT_DEPARTMENT (
                  DOCUMENT_ID
                , DEPARTMENT_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(document_id)s
                , %(department_id)s
                , %(assigned_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.DOCUMENT_DEPARTMENT
            SET
                  DOCUMENT_ID = %(document_id)s
                , DEPARTMENT_ID = %(department_id)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.DOCUMENT_DEPARTMENT
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

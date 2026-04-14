from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.publication_model import PublicationModel


class PublicationManager(DatabaseManager):

    def __init__(self):
        super().__init__(PublicationModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , TITLE
                , CONTENT
                , STATUS
                , CREATED_BY
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.PUBLICATION
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.PUBLICATION (
                  TITLE
                , CONTENT
                , STATUS
                , CREATED_BY
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            ) VALUES (
                  %(title)s
                , %(content)s
                , %(status)s
                , %(created_by)s
                , %(is_active)s
                , %(created_at)s
                , %(updated_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.PUBLICATION
            SET
                  TITLE = %(title)s
                , CONTENT = %(content)s
                , STATUS = %(status)s
                , CREATED_BY = %(created_by)s
                , IS_ACTIVE = %(is_active)s
                , UPDATED_AT = %(updated_at)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.PUBLICATION
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return data

    def _before_update(self, data: dict) -> dict:
        data["updated_at"] = datetime.now()
        return data

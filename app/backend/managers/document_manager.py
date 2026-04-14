from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.models.document_model import DocumentModel


class DocumentManager(DatabaseManager):

    def __init__(self):
        super().__init__(DocumentModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , TITLE
                , FILE_NAME
                , MIME_TYPE
                , FILE_SIZE
                , DESCRIPTION
                , UPLOADED_BY
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.DOCUMENT
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.DOCUMENT (
                  TITLE
                , FILE_NAME
                , FILE_BINARY
                , MIME_TYPE
                , FILE_SIZE
                , DESCRIPTION
                , UPLOADED_BY
                , IS_ACTIVE
                , CREATED_AT
                , UPDATED_AT
            ) VALUES (
                  %(title)s
                , %(file_name)s
                , %(file_binary)s
                , %(mime_type)s
                , %(file_size)s
                , %(description)s
                , %(uploaded_by)s
                , %(is_active)s
                , %(created_at)s
                , %(updated_at)s
            )
        """

    def _update_query(self):
        return """
            UPDATE PUBLIC.DOCUMENT
            SET
                  TITLE = %(title)s
                , FILE_NAME = %(file_name)s
                , MIME_TYPE = %(mime_type)s
                , FILE_SIZE = %(file_size)s
                , DESCRIPTION = %(description)s
                , UPLOADED_BY = %(uploaded_by)s
                , IS_ACTIVE = %(is_active)s
                , UPDATED_AT = %(updated_at)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.DOCUMENT
            WHERE ID = %(id)s
        """

    def _before_insert(self, data: dict) -> dict:
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return data

    def _before_update(self, data: dict) -> dict:
        data["updated_at"] = datetime.now()
        return data
    
    def get_document(self, id_doc: int):
        """
        Devuelve un documento almacenado dentro de la tabla.

        Args:
            id_doc (int): Id. del registro que contiene el documento.
        """
        sql = """
            SELECT
                  ID
                , FILE_NAME
                , FILE_BINARY
                , MIME_TYPE
            FROM PUBLIC.DOCUMENT
            WHERE ID = %(id)s
        """

        return self.fetchone(
            sql=sql,
            params={"id": id_doc},
            data_model=False
        )

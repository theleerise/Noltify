from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.core.database_connection import DatabaseConnection
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

    def get_accessible_document(self, document_id: int, user_id: int) -> dict | None:
        sql = """
            SELECT DISTINCT
                  DOC.ID
                , DOC.FILE_NAME
                , DOC.FILE_BINARY
                , DOC.MIME_TYPE
            FROM PUBLIC.DOCUMENT AS DOC
            WHERE DOC.ID = %(document_id)s
              AND DOC.IS_ACTIVE = TRUE
              AND (
                    DOC.UPLOADED_BY = %(user_id)s
                    OR EXISTS (
                        SELECT 1
                        FROM PUBLIC.DOCUMENT_USER AS DU_ACCESS
                        WHERE DU_ACCESS.DOCUMENT_ID = DOC.ID
                          AND DU_ACCESS.USER_ID = %(user_id)s
                    )
                    OR NOT EXISTS (
                        SELECT 1
                        FROM PUBLIC.DOCUMENT_DEPARTMENT AS DD_SCOPE
                        WHERE DD_SCOPE.DOCUMENT_ID = DOC.ID
                    )
                    OR EXISTS (
                        SELECT 1
                        FROM PUBLIC.DOCUMENT_DEPARTMENT AS DD_ACCESS
                        INNER JOIN PUBLIC.DEPARTMENT_USER AS DEUS
                            ON DEUS.DEPARTMENT_ID = DD_ACCESS.DEPARTMENT_ID
                        WHERE DD_ACCESS.DOCUMENT_ID = DOC.ID
                          AND DEUS.USER_ID = %(user_id)s
                    )
              )
            LIMIT 1
        """

        return self.fetchone(
            sql=sql,
            params={
                "document_id": document_id,
                "user_id": user_id,
            },
            data_model=False,
        )

    def get_user_departments(self, user_id: int) -> list[dict]:
        sql = """
            SELECT DISTINCT
                  DE.ID
                , DE.CODE
                , DE.NAME
            FROM PUBLIC.DEPARTMENT_USER AS DEUS
            INNER JOIN PUBLIC.DEPARTMENT AS DE
                ON DE.ID = DEUS.DEPARTMENT_ID
            WHERE DEUS.USER_ID = %(user_id)s
              AND DE.IS_ACTIVE = TRUE
            ORDER BY DE.CODE ASC, DE.NAME ASC, DE.ID ASC
        """

        return self.fetchall(
            sql=sql,
            params={"user_id": user_id},
            data_model=False,
        )

    def user_belongs_to_department(self, user_id: int, department_id: int) -> bool:
        sql = """
            SELECT 1 AS EXISTS_ROW
            FROM PUBLIC.DEPARTMENT_USER
            WHERE USER_ID = %(user_id)s
              AND DEPARTMENT_ID = %(department_id)s
            LIMIT 1
        """

        record = self.fetchone(
            sql=sql,
            params={
                "user_id": user_id,
                "department_id": department_id,
            },
            data_model=False,
        )

        return bool(record)

    def get_general_documents_page(
        self,
        *,
        scope: str,
        user_id: int,
        page: int = 1,
        order_by: dict[str, str] | None = None,
        department_id: int | None = None,
    ) -> dict:
        sql = self._build_general_documents_query(
            scope=scope,
            user_id=user_id,
            department_id=department_id,
        )

        return self.get_list_page(
            sql=sql,
            order_by=order_by,
            page=page,
            data_model=False,
        )

    def _build_general_documents_query(
        self,
        *,
        scope: str,
        user_id: int,
        department_id: int | None = None,
    ) -> str:
        if scope == "department":
            if department_id is None:
                raise ValueError("Debes indicar un departamento para consultar documentos por departamento.")

            scope_condition = f"""
                EXISTS (
                    SELECT 1
                    FROM PUBLIC.DOCUMENT_DEPARTMENT AS DD_SCOPE
                    WHERE DD_SCOPE.DOCUMENT_ID = DOC.ID
                      AND DD_SCOPE.DEPARTMENT_ID = {int(department_id)}
                )
            """
        elif scope == "general":
            scope_condition = """
                NOT EXISTS (
                    SELECT 1
                    FROM PUBLIC.DOCUMENT_DEPARTMENT AS DD_SCOPE
                    WHERE DD_SCOPE.DOCUMENT_ID = DOC.ID
                )
            """
        elif scope == "user":
            scope_condition = f"DOC.UPLOADED_BY = {int(user_id)}"
        elif scope == "assigned_user":
            scope_condition = f"""
                EXISTS (
                    SELECT 1
                    FROM PUBLIC.DOCUMENT_USER AS DU_SCOPE
                    WHERE DU_SCOPE.DOCUMENT_ID = DOC.ID
                      AND DU_SCOPE.USER_ID = {int(user_id)}
                )
            """
        else:
            raise ValueError("El scope indicado para documentos generales no es valido.")

        return f"""
            SELECT DISTINCT
                  DOC.ID
                , DOC.TITLE
                , DOC.FILE_NAME
                , DOC.MIME_TYPE
                , DOC.FILE_SIZE
                , DOC.DESCRIPTION
                , DOC.UPLOADED_BY
                , DOC.IS_ACTIVE
                , DOC.CREATED_AT
                , DOC.UPDATED_AT
            FROM PUBLIC.DOCUMENT AS DOC
            WHERE DOC.IS_ACTIVE = TRUE
              AND {scope_condition}
        """

    def create_document_for_user(
        self,
        *,
        document_data: dict,
        uploaded_by: int,
        department_id: int | None = None,
    ) -> dict:
        final_data = self._before_insert({
            **document_data,
            "uploaded_by": uploaded_by,
        })

        insert_document_sql = """
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
            RETURNING ID
        """

        insert_department_sql = """
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

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(insert_document_sql, final_data)
                new_document = cursor.fetchone() or {}
                document_id = new_document.get("id")

                if department_id is not None:
                    cursor.execute(
                        insert_department_sql,
                        {
                            "document_id": document_id,
                            "department_id": department_id,
                            "assigned_at": datetime.now(),
                        },
                    )

            connection.commit()

        self._after_insert(final_data)

        return {"id": document_id}

    def get_owned_document(self, document_id: int, uploaded_by: int) -> dict | None:
        sql = """
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
            WHERE ID = %(id)s
              AND UPLOADED_BY = %(uploaded_by)s
            LIMIT 1
        """

        return self.fetchone(
            sql=sql,
            params={
                "id": document_id,
                "uploaded_by": uploaded_by,
            },
            data_model=False,
        )

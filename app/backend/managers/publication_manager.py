from datetime import datetime

from backend.core.database_connection import DatabaseConnection
from backend.core.database_manager import DatabaseManager
from backend.models.publication_model import PublicationModel


class PublicationManager(DatabaseManager):

    def __init__(self):
        super().__init__(PublicationModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  PUB.ID
                , PUB.TITLE
                , PUB.CONTENT
                , PUB.STATUS
                , PUB.CREATED_BY
                , CONCAT(
                    US.USERNAME,
                    CASE
                        WHEN COALESCE(US.FIRST_NAME, '') <> '' OR COALESCE(US.LAST_NAME, '') <> ''
                            THEN CONCAT(' (', TRIM(CONCAT(COALESCE(US.FIRST_NAME, ''), ' ', COALESCE(US.LAST_NAME, ''))), ')')
                        ELSE ''
                    END
                ) AS CREATED_BY_DISPLAY
                , PUB.IS_ACTIVE
                , PUB.CREATED_AT
                , PUB.UPDATED_AT
            FROM PUBLIC.PUBLICATION AS PUB
            LEFT JOIN PUBLIC.APP_USER AS US
                ON US.ID = PUB.CREATED_BY
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

    def get_general_publications_page(
        self,
        *,
        scope: str,
        user_id: int,
        page: int = 1,
        order_by: dict[str, str] | None = None,
        department_id: int | None = None,
    ) -> dict:
        sql = self._build_general_publications_query(
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

    def _build_general_publications_query(
        self,
        *,
        scope: str,
        user_id: int,
        department_id: int | None = None,
    ) -> str:
        if scope == "department":
            if department_id is None:
                raise ValueError("Debes indicar un departamento para consultar publicaciones por departamento.")

            scope_condition = f"""
                EXISTS (
                    SELECT 1
                    FROM PUBLIC.PUBLICATION_DEPARTMENT AS PD_SCOPE
                    WHERE PD_SCOPE.PUBLICATION_ID = PUB.ID
                      AND PD_SCOPE.DEPARTMENT_ID = {int(department_id)}
                )
            """
        elif scope == "general":
            scope_condition = """
                NOT EXISTS (
                    SELECT 1
                    FROM PUBLIC.PUBLICATION_DEPARTMENT AS PD_SCOPE
                    WHERE PD_SCOPE.PUBLICATION_ID = PUB.ID
                )
            """
        elif scope == "user":
            scope_condition = f"PUB.CREATED_BY = {int(user_id)}"
        elif scope == "assigned_user":
            scope_condition = f"""
                EXISTS (
                    SELECT 1
                    FROM PUBLIC.PUBLICATION_USER AS PU_SCOPE
                    WHERE PU_SCOPE.PUBLICATION_ID = PUB.ID
                      AND PU_SCOPE.USER_ID = {int(user_id)}
                )
            """
        else:
            raise ValueError("El scope indicado para publicaciones generales no es valido.")

        return f"""
            SELECT DISTINCT
                  PUB.ID
                , PUB.TITLE
                , PUB.CONTENT
                , PUB.STATUS
                , PUB.CREATED_BY
                , CONCAT(
                    US.USERNAME,
                    CASE
                        WHEN COALESCE(US.FIRST_NAME, '') <> '' OR COALESCE(US.LAST_NAME, '') <> ''
                            THEN CONCAT(' (', TRIM(CONCAT(COALESCE(US.FIRST_NAME, ''), ' ', COALESCE(US.LAST_NAME, ''))), ')')
                        ELSE ''
                    END
                ) AS CREATED_BY_DISPLAY
                , PUB.IS_ACTIVE
                , PUB.CREATED_AT
                , PUB.UPDATED_AT
            FROM PUBLIC.PUBLICATION AS PUB
            LEFT JOIN PUBLIC.APP_USER AS US
                ON US.ID = PUB.CREATED_BY
            WHERE PUB.IS_ACTIVE = TRUE
              AND {scope_condition}
        """

    def create_publication_for_user(
        self,
        *,
        publication_data: dict,
        created_by: int,
        department_id: int | None = None,
    ) -> dict:
        final_data = self._before_insert({
            **publication_data,
            "created_by": created_by,
        })

        insert_publication_sql = """
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
            RETURNING ID
        """

        insert_department_sql = """
            INSERT INTO PUBLIC.PUBLICATION_DEPARTMENT (
                  PUBLICATION_ID
                , DEPARTMENT_ID
                , ASSIGNED_AT
            ) VALUES (
                  %(publication_id)s
                , %(department_id)s
                , %(assigned_at)s
            )
        """

        with DatabaseConnection.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(insert_publication_sql, final_data)
                new_publication = cursor.fetchone() or {}
                publication_id = new_publication.get("id")

                if department_id is not None:
                    cursor.execute(
                        insert_department_sql,
                        {
                            "publication_id": publication_id,
                            "department_id": department_id,
                            "assigned_at": datetime.now(),
                        },
                    )

            connection.commit()

        self._after_insert(final_data)

        return {"id": publication_id}

    def get_owned_publication(self, publication_id: int, created_by: int) -> dict | None:
        sql = """
            SELECT
                  PUB.ID
                , PUB.TITLE
                , PUB.CONTENT
                , PUB.STATUS
                , PUB.CREATED_BY
                , PUB.IS_ACTIVE
                , PUB.CREATED_AT
                , PUB.UPDATED_AT
            FROM PUBLIC.PUBLICATION AS PUB
            WHERE PUB.ID = %(id)s
              AND PUB.CREATED_BY = %(created_by)s
            LIMIT 1
        """

        return self.fetchone(
            sql=sql,
            params={
                "id": publication_id,
                "created_by": created_by,
            },
            data_model=False,
        )

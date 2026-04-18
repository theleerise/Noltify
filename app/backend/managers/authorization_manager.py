from __future__ import annotations

from backend.core.database_manager import DatabaseManager


class AuthorizationManager(DatabaseManager):

    def __init__(self):
        super().__init__(model=None, primary_key="id", rows_page=10)

    def get_role_codes(self, user_id: int) -> set[str]:
        sql = """
            SELECT DISTINCT RO.CODE
            FROM PUBLIC.ROLE_USER AS RU
            INNER JOIN PUBLIC.ROLE AS RO
                ON RO.ID = RU.ROLE_ID
            WHERE RU.USER_ID = %(user_id)s
              AND COALESCE(RO.IS_ACTIVE, TRUE) = TRUE
        """
        rows = self.fetchall(sql=sql, params={"user_id": user_id}, data_model=False)
        return {
            str(row.get("code")).strip().upper()
            for row in rows
            if row.get("code")
        }

    def get_permission_codes(self, user_id: int) -> set[str]:
        sql = """
            SELECT DISTINCT PERMISSION_CODE
            FROM (
                SELECT PE.CODE AS PERMISSION_CODE
                FROM PUBLIC.PERMISSION_USER AS PU
                INNER JOIN PUBLIC.PERMISSION AS PE
                    ON PE.ID = PU.PERMISSION_ID
                WHERE PU.USER_ID = %(user_id)s
                  AND COALESCE(PE.IS_ACTIVE, TRUE) = TRUE

                UNION

                SELECT PE.CODE AS PERMISSION_CODE
                FROM PUBLIC.ROLE_USER AS RU
                INNER JOIN PUBLIC.ROLE AS RO
                    ON RO.ID = RU.ROLE_ID
                INNER JOIN PUBLIC.ROLE_PERMISSION AS RP
                    ON RP.ROLE_ID = RO.ID
                INNER JOIN PUBLIC.PERMISSION AS PE
                    ON PE.ID = RP.PERMISSION_ID
                WHERE RU.USER_ID = %(user_id)s
                  AND COALESCE(RO.IS_ACTIVE, TRUE) = TRUE
                  AND COALESCE(PE.IS_ACTIVE, TRUE) = TRUE
            ) AS ACCESS_PERMISSIONS
        """
        rows = self.fetchall(sql=sql, params={"user_id": user_id}, data_model=False)
        return {
            str(row.get("permission_code")).strip().upper()
            for row in rows
            if row.get("permission_code")
        }

    def get_access_profile(self, user_id: int) -> dict[str, set[str]]:
        return {
            "role_codes": self.get_role_codes(user_id),
            "permission_codes": self.get_permission_codes(user_id),
        }

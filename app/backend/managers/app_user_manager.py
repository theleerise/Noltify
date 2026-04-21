from datetime import datetime

from django.contrib.auth.hashers import make_password

from backend.core.database_manager import DatabaseManager
from backend.models.app_user_model import AppUserModel


class AppUserManager(DatabaseManager):

    def __init__(self):
        super().__init__(AppUserModel, "id", rows_page=10)

    def _select_query(self) -> str:
        return """
            SELECT
                  ID
                , USERNAME
                , EMAIL
                , FIRST_NAME
                , LAST_NAME
                , IS_ACTIVE
                , IS_SUPERUSER
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.APP_USER
            WHERE 1 = 1
        """

    def _insert_query(self):
        return """
            INSERT INTO PUBLIC.APP_USER (
                  USERNAME
                , EMAIL
                , PASSWORD_HASH
                , FIRST_NAME
                , LAST_NAME
                , IS_ACTIVE
                , IS_SUPERUSER
                , CREATED_AT
                , UPDATED_AT
            ) VALUES (
                  %(username)s
                , %(email)s
                , %(password_hash)s
                , %(first_name)s
                , %(last_name)s
                , %(is_active)s
                , %(is_superuser)s
                , %(created_at)s
                , %(updated_at)s
            )
        """

    def _update_query(self, include_password: bool = False):
        password_sql = ""
        if include_password:
            password_sql = "\n                , PASSWORD_HASH = %(password_hash)s"

        return f"""
            UPDATE PUBLIC.APP_USER
            SET
                  USERNAME = %(username)s
                , EMAIL = %(email)s{password_sql}
                , FIRST_NAME = %(first_name)s
                , LAST_NAME = %(last_name)s
                , IS_ACTIVE = %(is_active)s
                , IS_SUPERUSER = %(is_superuser)s
                , UPDATED_AT = %(updated_at)s
            WHERE ID = %(id)s
        """

    def _delete_query(self):
        return """
            DELETE FROM PUBLIC.APP_USER
            WHERE ID = %(id)s
        """

    def get_by_login(self, login_value: str):
        normalized_login = (login_value or "").strip()
        if not normalized_login:
            return None

        sql = """
            SELECT
                  ID
                , USERNAME
                , EMAIL
                , PASSWORD_HASH
                , FIRST_NAME
                , LAST_NAME
                , IS_ACTIVE
                , IS_SUPERUSER
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.APP_USER
            WHERE IS_ACTIVE = TRUE
              AND (
                    UPPER(USERNAME) = UPPER(%(login_value)s)
                 OR UPPER(EMAIL) = UPPER(%(login_value)s)
              )
            ORDER BY ID ASC
            LIMIT 1
        """

        return self.fetchone(sql=sql, params={"login_value": normalized_login}, data_model=False)

    def get_by_username(self, username: str, *, exclude_id: int | None = None):
        normalized_username = (username or "").strip()
        if not normalized_username:
            return None

        sql = """
            SELECT
                  ID
                , USERNAME
                , EMAIL
                , PASSWORD_HASH
                , FIRST_NAME
                , LAST_NAME
                , IS_ACTIVE
                , IS_SUPERUSER
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.APP_USER
            WHERE UPPER(USERNAME) = UPPER(%(username)s)
        """

        params = {"username": normalized_username}
        if exclude_id is not None:
            sql += "\n              AND ID <> %(exclude_id)s"
            params["exclude_id"] = exclude_id

        sql += "\n            ORDER BY ID ASC\n            LIMIT 1"

        return self.fetchone(sql=sql, params=params, data_model=False)

    def get_by_email(self, email: str, *, exclude_id: int | None = None):
        normalized_email = (email or "").strip()
        if not normalized_email:
            return None

        sql = """
            SELECT
                  ID
                , USERNAME
                , EMAIL
                , PASSWORD_HASH
                , FIRST_NAME
                , LAST_NAME
                , IS_ACTIVE
                , IS_SUPERUSER
                , CREATED_AT
                , UPDATED_AT
            FROM PUBLIC.APP_USER
            WHERE UPPER(EMAIL) = UPPER(%(email)s)
        """

        params = {"email": normalized_email}
        if exclude_id is not None:
            sql += "\n              AND ID <> %(exclude_id)s"
            params["exclude_id"] = exclude_id

        sql += "\n            ORDER BY ID ASC\n            LIMIT 1"

        return self.fetchone(sql=sql, params=params, data_model=False)

    def insert_query(self, data: dict):
        final_data = self._before_insert(data)
        self.execute_query_data(
            sql=self._insert_query(),
            params=final_data,
        )
        self._after_insert(final_data)

    def update_query(self, data: dict):
        final_data = self._before_update(data)
        include_password = "password_hash" in final_data

        self.execute_query_data(
            sql=self._update_query(include_password=include_password),
            params=final_data,
        )

        self._after_update(final_data)

    def _before_insert(self, data: dict) -> dict:
        password = self._normalize_password(data.get("password_hash"))
        if not password:
            raise ValueError("La contrasena es obligatoria para crear un usuario.")

        data["password_hash"] = make_password(password)
        return self._apply_timestamp_audit_on_insert(data)

    def _before_update(self, data: dict) -> dict:
        password = self._normalize_password(data.get("password_hash"))

        if password:
            data["password_hash"] = make_password(password)
        else:
            data.pop("password_hash", None)

        return self._apply_timestamp_audit_on_update(data)

    @staticmethod
    def _normalize_password(password: str | None) -> str | None:
        if password is None:
            return None

        normalized_password = password.strip()
        return normalized_password or None

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

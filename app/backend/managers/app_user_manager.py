from datetime import datetime

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
                , PASSWORD_HASH
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

    def _update_query(self):
        return """
            UPDATE PUBLIC.APP_USER
            SET
                  USERNAME = %(username)s
                , EMAIL = %(email)s
                , PASSWORD_HASH = %(password_hash)s
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

    def _before_insert(self, data: dict) -> dict:
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return data

    def _before_update(self, data: dict) -> dict:
        data["updated_at"] = datetime.now()
        return data

from backend.core.database_manager import DatabaseManager
from backend.models.department_model import DepartmentModel


class ApiValueManager(DatabaseManager):

    QUERY_PREFIX = "_query_"

    def __init__(self):
        super().__init__(DepartmentModel, "id", rows_page=10)

    def get_master(self, master_name: str) -> str:
        """
        Devuelve la SQL registrada para el master indicado.

        Ejemplo:
            mgr = ApiValueManager()
            query = mgr.get_master("DEPARTMENTS")
        """
        if not isinstance(master_name, str) or not master_name.strip():
            raise ValueError("master_name debe ser un string no vacío")

        normalized_name = master_name.strip().upper()
        method_name = f"{self.QUERY_PREFIX}{normalized_name}"

        query_method = getattr(self, method_name, None)

        if query_method is None or not callable(query_method):
            available_masters = ", ".join(self.list_masters())
            raise ValueError(
                f"No existe un master registrado con el nombre '{normalized_name}'. "
                f"Masters disponibles: [{available_masters}]"
            )

        return query_method()

    def has_master(self, master_name: str) -> bool:
        """
        Indica si existe un master registrado.
        """
        if not isinstance(master_name, str) or not master_name.strip():
            return False

        normalized_name = master_name.strip().upper()
        method_name = f"{self.QUERY_PREFIX}{normalized_name}"
        query_method = getattr(self, method_name, None)

        return query_method is not None and callable(query_method)

    def list_masters(self) -> list[str]:
        """
        Devuelve el listado de masters registrados en la clase.
        """
        masters = []

        for attr_name in dir(self):
            if attr_name.startswith(self.QUERY_PREFIX):
                query_method = getattr(self, attr_name, None)
                if callable(query_method):
                    masters.append(attr_name[len(self.QUERY_PREFIX):])

        masters.sort()
        return masters
    
    def _query_DEPARTMENTS(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , CODE AS DISPLAY_VALUE
                FROM PUBLIC.DEPARTMENT
            ) WHERE 1=1
        """
        return query

    def _query_APP_USERS(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , CONCAT(USERNAME, ' (', FIRST_NAME, ' ', LAST_NAME, ')') AS DISPLAY_VALUE
                FROM PUBLIC.APP_USER
            ) WHERE 1=1
        """
        return query

    def _query_DOCUMENTS(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , TITLE AS DISPLAY_VALUE
                FROM PUBLIC.DOCUMENT
            ) WHERE 1=1
        """
        return query

    def _query_PERMISSIONS(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , CODE AS DISPLAY_VALUE
                FROM PUBLIC.PERMISSION
            ) WHERE 1=1
        """
        return query

    def _query_PUBLICATIONS(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , TITLE AS DISPLAY_VALUE
                FROM PUBLIC.PUBLICATION
            ) WHERE 1=1
        """
        return query

    def _query_ROLES(self) -> str:
        query = """
            SELECT
                  ID_ROW
                , DISPLAY_VALUE
            FROM (
                SELECT
                      ID AS ID_ROW
                    , CODE AS DISPLAY_VALUE
                FROM PUBLIC.ROLE
            ) WHERE 1=1
        """
        return query

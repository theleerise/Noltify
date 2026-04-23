"""
Manager de acceso a datos para document.

Este módulo concentra las consultas y operaciones de persistencia asociadas a la entidad o relación correspondiente.
"""

from datetime import datetime

from backend.core.database_manager import DatabaseManager
from backend.core.database_connection import DatabaseConnection
from backend.models.document_model import DocumentModel


class DocumentManager(DatabaseManager):
    """
    Manager encargado de encapsular las operaciones de acceso a datos de la entidad asociada.

    Esta clase centraliza las consultas SQL, los ajustes previos a inserción o actualización y cualquier comportamiento adicional requerido por la entidad.
    """

    def __init__(self):
        """
        Inicializa el manager con la configuración base de la entidad.

        Returns:
            None: El método deja preparada la clase base con el modelo, la clave primaria y la configuración de paginación necesarias.
        """
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
        """
        Ajusta los datos antes de insertar un documento.

        Args:
            data (dict): Información del documento que se desea persistir.

        Returns:
            dict: Diccionario final con las marcas temporales necesarias para la
            inserción.
        """
        return self._apply_timestamp_audit_on_insert(data)

    def _before_update(self, data: dict) -> dict:
        """
        Ajusta los datos antes de actualizar un documento existente.

        Además de actualizar la auditoría temporal, elimina el campo
        `uploaded_by` para evitar que se modifique durante una edición.

        Args:
            data (dict): Datos recibidos para la actualización.

        Returns:
            dict: Diccionario final preparado para la operación de actualización.
        """
        data = self._apply_timestamp_audit_on_update(data)
        data.pop("uploaded_by", None)
        return data

    @staticmethod
    def _apply_timestamp_audit_on_insert(data: dict) -> dict:
        """
        Añade las fechas de creación y actualización a un documento nuevo.

        Args:
            data (dict): Datos del documento que se va a insertar.

        Returns:
            dict: Diccionario con las marcas temporales incorporadas.
        """
        now = datetime.now()
        data["created_at"] = now
        data["updated_at"] = now
        return data

    @staticmethod
    def _apply_timestamp_audit_on_update(data: dict) -> dict:
        """
        Actualiza la fecha de modificación de un documento.

        Args:
            data (dict): Datos del documento que se va a actualizar.

        Returns:
            dict: Diccionario con la fecha de actualización renovada.
        """
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
        """
        Recupera un documento únicamente si el usuario tiene acceso a él.

        El acceso se considera válido cuando el documento pertenece al usuario,
        ha sido asignado de forma directa, está disponible por departamento o
        forma parte del ámbito general visible.

        Args:
            document_id (int): Identificador del documento solicitado.
            user_id (int): Identificador del usuario que intenta acceder.

        Returns:
            dict | None: Registro del documento si el usuario puede acceder o
            `None` si no cumple las condiciones de visibilidad.
        """
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
                    AND NOT EXISTS (
                        SELECT 1
                        FROM PUBLIC.DOCUMENT_USER AS DU_SCOPE
                        WHERE DU_SCOPE.DOCUMENT_ID = DOC.ID
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
        """
        Recupera los departamentos activos a los que pertenece un usuario.

        Args:
            user_id (int): Identificador del usuario del que se quieren obtener
                los departamentos.

        Returns:
            list[dict]: Lista de departamentos activos asociados al usuario.
        """
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
        """
        Comprueba si un usuario pertenece a un departamento concreto.

        Args:
            user_id (int): Identificador del usuario que se desea comprobar.
            department_id (int): Identificador del departamento a validar.

        Returns:
            bool: `True` si existe la relación usuario-departamento, `False` en
            caso contrario.
        """
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
        """
        Recupera una página de documentos visibles según un ámbito determinado.

        El ámbito puede represetar documentos generales, por departamento, del
        propio usuario o asignados explícitamente al usuario.

        Args:
            scope (str): Tipo de ámbito sobre el que se realizará la consulta.
            user_id (int): Identificador del usuario para resolver el contexto
                de visibilidad.
            page (int): Página que se desea recuperar.
            order_by (dict[str, str] | None): Configuración de ordenación del
                listado.
            department_id (int | None): Departamento aplicado cuando el ámbito
                depende de un departamento concreto.

        Returns:
            dict: Estructura paginada con los documentos visibles según el
            ámbito indicado.
        """
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
        """
        Construye la consulta base de documentos visibles para un ámbito.

        Args:
            scope (str): Ámbito de visibilidad que determina el filtro
                principal.
            user_id (int): Identificador del usuario utilizado para resolver
                pertenencias y asignaciones.
            department_id (int | None): Identificador del departamento cuando el
                ámbito es departamental.

        Returns:
            str: Consulta SQL lista para usarse en listados paginados de
            documentos.
        """
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
                AND NOT EXISTS (
                    SELECT 1
                    FROM PUBLIC.DOCUMENT_USER AS DU_SCOPE
                    WHERE DU_SCOPE.DOCUMENT_ID = DOC.ID
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
        """
        Crea un documento vinculado a un usuario y opcionalmente a un departamento.

        El método inserta el documento principal y, si se informa un
        departamento, registra también la asociación en la tabla relacional.

        Args:
            document_data (dict): Datos del documento que se desea crear.
            uploaded_by (int): Identificador del usuario que realiza la carga.
            department_id (int | None): Departamento al que se asociará el
                documento, si corresponde.

        Returns:
            dict: Diccionario con el identificador del documento recién creado.
        """
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
        """
        Recupera un documento solo si pertenece al usuario indicado.

        Args:
            document_id (int): Identificador del documento que se desea obtener.
            uploaded_by (int): Identificador del usuario propietario esperado.

        Returns:
            dict | None: Registro del documento si pertenece al usuario o
            `None` si no existe esa correspondencia.
        """
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


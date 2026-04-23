"""
Manager de acceso a datos para authorization.

Este módulo concentra las consultas y operaciones de persistencia asociadas a la entidad o relación correspondiente.
"""

from __future__ import annotations

from backend.core.database_manager import DatabaseManager


class AuthorizationManager(DatabaseManager):
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
        super().__init__(model=None, primary_key="id", rows_page=10)

    def get_role_codes(self, user_id: int) -> set[str]:
        """
        Recupera los códigos de rol asignados a un usuario.

        La consulta busca los roles vinculados al usuario y devuelve sus códigos
        normalizados en mayúsculas para facilitar las validaciones de acceso.

        Args:
            user_id (int): Identificador del usuario del que se desean obtener
                los roles.

        Returns:
            set[str]: Conjunto de códigos de rol activos asociados al usuario.
        """
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
        """
        Recupera todos los permisos disponibles para un usuario.

        El resultado combina los permisos asignados directamente al usuario con
        aquellos heredados a través de sus roles activos.

        Args:
            user_id (int): Identificador del usuario del que se desean obtener
                los permisos.

        Returns:
            set[str]: Conjunto de códigos de permisos activos asociados al
            usuario.
        """
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
        """
        Construye el perfil de acceso completo de un usuario.

        Este método unifica en una única estructura los roles y permisos que
        podrán utilizarse posteriormente durante las comprobaciones de
        autorización.

        Args:
            user_id (int): Identificador del usuario del que se construirá el
                perfil de acceso.

        Returns:
            dict[str, set[str]]: Diccionario con los conjuntos `role_codes` y
            `permission_codes` del usuario.
        """
        return {
            "role_codes": self.get_role_codes(user_id),
            "permission_codes": self.get_permission_codes(user_id),
        }


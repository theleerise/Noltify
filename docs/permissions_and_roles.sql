
BEGIN;

-- =========================================================
-- PERMISSION
-- =========================================================
WITH PERMISSION_SEED(CODE, NAME, DESCRIPTION) AS (
    VALUES
        ('APP_USER_LIST', 'Listar usuarios', 'Permite visualizar el listado de usuarios.'),
        ('APP_USER_INSERT', 'Crear usuarios', 'Permite crear usuarios.'),
        ('APP_USER_UPDATE', 'Editar usuarios', 'Permite modificar usuarios.'),
        ('APP_USER_DELETE', 'Eliminar usuarios', 'Permite eliminar usuarios.'),

        ('DEPARTMENT_LIST', 'Listar departamentos', 'Permite visualizar el listado de departamentos.'),
        ('DEPARTMENT_INSERT', 'Crear departamentos', 'Permite crear departamentos.'),
        ('DEPARTMENT_UPDATE', 'Editar departamentos', 'Permite modificar departamentos.'),
        ('DEPARTMENT_DELETE', 'Eliminar departamentos', 'Permite eliminar departamentos.'),

        ('DEPARTMENT_USER_LIST', 'Listar asignaciones departamento-usuario', 'Permite visualizar asignaciones entre departamentos y usuarios.'),
        ('DEPARTMENT_USER_INSERT', 'Crear asignaciones departamento-usuario', 'Permite crear asignaciones entre departamentos y usuarios.'),
        ('DEPARTMENT_USER_UPDATE', 'Editar asignaciones departamento-usuario', 'Permite modificar asignaciones entre departamentos y usuarios.'),
        ('DEPARTMENT_USER_DELETE', 'Eliminar asignaciones departamento-usuario', 'Permite eliminar asignaciones entre departamentos y usuarios.'),

        ('DOCUMENT_LIST', 'Listar documentos', 'Permite visualizar documentos y acceder a la vista general de documentos.'),
        ('DOCUMENT_INSERT', 'Crear documentos', 'Permite crear documentos.'),
        ('DOCUMENT_UPDATE', 'Editar documentos', 'Permite modificar documentos.'),
        ('DOCUMENT_DELETE', 'Eliminar documentos', 'Permite eliminar documentos.'),

        ('DOCUMENT_DEPARTMENT_LIST', 'Listar asignaciones documento-departamento', 'Permite visualizar asignaciones entre documentos y departamentos.'),
        ('DOCUMENT_DEPARTMENT_INSERT', 'Crear asignaciones documento-departamento', 'Permite crear asignaciones entre documentos y departamentos.'),
        ('DOCUMENT_DEPARTMENT_UPDATE', 'Editar asignaciones documento-departamento', 'Permite modificar asignaciones entre documentos y departamentos.'),
        ('DOCUMENT_DEPARTMENT_DELETE', 'Eliminar asignaciones documento-departamento', 'Permite eliminar asignaciones entre documentos y departamentos.'),

        ('DOCUMENT_USER_LIST', 'Listar asignaciones documento-usuario', 'Permite visualizar asignaciones entre documentos y usuarios.'),
        ('DOCUMENT_USER_INSERT', 'Crear asignaciones documento-usuario', 'Permite crear asignaciones entre documentos y usuarios.'),
        ('DOCUMENT_USER_UPDATE', 'Editar asignaciones documento-usuario', 'Permite modificar asignaciones entre documentos y usuarios.'),
        ('DOCUMENT_USER_DELETE', 'Eliminar asignaciones documento-usuario', 'Permite eliminar asignaciones entre documentos y usuarios.'),

        ('PERMISSION_LIST', 'Listar permisos', 'Permite visualizar el listado de permisos.'),
        ('PERMISSION_INSERT', 'Crear permisos', 'Permite crear permisos.'),
        ('PERMISSION_UPDATE', 'Editar permisos', 'Permite modificar permisos.'),
        ('PERMISSION_DELETE', 'Eliminar permisos', 'Permite eliminar permisos.'),

        ('PERMISSION_USER_LIST', 'Listar asignaciones permiso-usuario', 'Permite visualizar asignaciones entre permisos y usuarios.'),
        ('PERMISSION_USER_INSERT', 'Crear asignaciones permiso-usuario', 'Permite crear asignaciones entre permisos y usuarios.'),
        ('PERMISSION_USER_UPDATE', 'Editar asignaciones permiso-usuario', 'Permite modificar asignaciones entre permisos y usuarios.'),
        ('PERMISSION_USER_DELETE', 'Eliminar asignaciones permiso-usuario', 'Permite eliminar asignaciones entre permisos y usuarios.'),

        ('PUBLICATION_LIST', 'Listar publicaciones', 'Permite visualizar publicaciones y acceder a la vista general de publicaciones.'),
        ('PUBLICATION_INSERT', 'Crear publicaciones', 'Permite crear publicaciones.'),
        ('PUBLICATION_UPDATE', 'Editar publicaciones', 'Permite modificar publicaciones.'),
        ('PUBLICATION_DELETE', 'Eliminar publicaciones', 'Permite eliminar publicaciones.'),

        ('PUBLICATION_DEPARTMENT_LIST', 'Listar asignaciones publicacion-departamento', 'Permite visualizar asignaciones entre publicaciones y departamentos.'),
        ('PUBLICATION_DEPARTMENT_INSERT', 'Crear asignaciones publicacion-departamento', 'Permite crear asignaciones entre publicaciones y departamentos.'),
        ('PUBLICATION_DEPARTMENT_UPDATE', 'Editar asignaciones publicacion-departamento', 'Permite modificar asignaciones entre publicaciones y departamentos.'),
        ('PUBLICATION_DEPARTMENT_DELETE', 'Eliminar asignaciones publicacion-departamento', 'Permite eliminar asignaciones entre publicaciones y departamentos.'),

        ('PUBLICATION_USER_LIST', 'Listar asignaciones publicacion-usuario', 'Permite visualizar asignaciones entre publicaciones y usuarios.'),
        ('PUBLICATION_USER_INSERT', 'Crear asignaciones publicacion-usuario', 'Permite crear asignaciones entre publicaciones y usuarios.'),
        ('PUBLICATION_USER_UPDATE', 'Editar asignaciones publicacion-usuario', 'Permite modificar asignaciones entre publicaciones y usuarios.'),
        ('PUBLICATION_USER_DELETE', 'Eliminar asignaciones publicacion-usuario', 'Permite eliminar asignaciones entre publicaciones y usuarios.'),

        ('ROLE_LIST', 'Listar roles', 'Permite visualizar el listado de roles.'),
        ('ROLE_INSERT', 'Crear roles', 'Permite crear roles.'),
        ('ROLE_UPDATE', 'Editar roles', 'Permite modificar roles.'),
        ('ROLE_DELETE', 'Eliminar roles', 'Permite eliminar roles.'),

        ('ROLE_PERMISSION_LIST', 'Listar asignaciones rol-permiso', 'Permite visualizar asignaciones entre roles y permisos.'),
        ('ROLE_PERMISSION_INSERT', 'Crear asignaciones rol-permiso', 'Permite crear asignaciones entre roles y permisos.'),
        ('ROLE_PERMISSION_UPDATE', 'Editar asignaciones rol-permiso', 'Permite modificar asignaciones entre roles y permisos.'),
        ('ROLE_PERMISSION_DELETE', 'Eliminar asignaciones rol-permiso', 'Permite eliminar asignaciones entre roles y permisos.'),

        ('ROLE_USER_LIST', 'Listar asignaciones rol-usuario', 'Permite visualizar asignaciones entre roles y usuarios.'),
        ('ROLE_USER_INSERT', 'Crear asignaciones rol-usuario', 'Permite crear asignaciones entre roles y usuarios.'),
        ('ROLE_USER_UPDATE', 'Editar asignaciones rol-usuario', 'Permite modificar asignaciones entre roles y usuarios.'),
        ('ROLE_USER_DELETE', 'Eliminar asignaciones rol-usuario', 'Permite eliminar asignaciones entre roles y usuarios.')
)
INSERT INTO PUBLIC.PERMISSION (
      CODE
    , NAME
    , DESCRIPTION
    , IS_ACTIVE
    , CREATED_AT
    , UPDATED_AT
)
SELECT
      S.CODE
    , S.NAME
    , S.DESCRIPTION
    , TRUE
    , NOW()
    , NOW()
FROM PERMISSION_SEED S
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.PERMISSION P
    WHERE P.CODE = S.CODE
);

-- =========================================================
-- ROLE
-- =========================================================
WITH ROLE_SEED(CODE, NAME, DESCRIPTION) AS (
    VALUES
        ('ADMIN_GENERAL', 'Administrador general', 'Rol que habilita la visualizacion del menu administrativo y concentra permisos de gestion global.'),

        ('DOCUMENT_VIEW', 'Visualizar documentos', 'Rol que permite visualizar documentos en la pantalla general de documentos.'),
        ('DOCUMENT_USER', 'Usuario de documentos adjuntos', 'Rol que permite visualizar y gestionar documentos propios.'),
        ('DOCUMENT_ADMIN', 'Administrador de documentos adjuntos', 'Rol que permite gestionar documentos y sus asignaciones a usuarios y departamentos.'),

        ('PUBLICATION_VIEW', 'Visualizar publicaciones', 'Rol que permite visualizar publicaciones en la pantalla general de publicaciones.'),
        ('PUBLICATION_USER', 'Usuario de publicaciones', 'Rol que permite visualizar y gestionar publicaciones propias.'),
        ('PUBLICATION_ADMIN', 'Administrador de publicaciones', 'Rol que permite gestionar publicaciones y sus asignaciones a usuarios y departamentos.')
)
INSERT INTO PUBLIC.ROLE (
      CODE
    , NAME
    , DESCRIPTION
    , IS_ACTIVE
    , CREATED_AT
    , UPDATED_AT
)
SELECT
      S.CODE
    , S.NAME
    , S.DESCRIPTION
    , TRUE
    , NOW()
    , NOW()
FROM ROLE_SEED S
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.ROLE R
    WHERE R.CODE = S.CODE
);

-- =========================================================
-- ROLE_PERMISSION
-- =========================================================
WITH ROLE_PERMISSION_SEED(ROLE_CODE, PERMISSION_CODE) AS (
    VALUES
        -- ADMIN_GENERAL: acceso total a toda la app
        ('ADMIN_GENERAL', 'APP_USER_LIST'),
        ('ADMIN_GENERAL', 'APP_USER_INSERT'),
        ('ADMIN_GENERAL', 'APP_USER_UPDATE'),
        ('ADMIN_GENERAL', 'APP_USER_DELETE'),

        ('ADMIN_GENERAL', 'DEPARTMENT_LIST'),
        ('ADMIN_GENERAL', 'DEPARTMENT_INSERT'),
        ('ADMIN_GENERAL', 'DEPARTMENT_UPDATE'),
        ('ADMIN_GENERAL', 'DEPARTMENT_DELETE'),

        ('ADMIN_GENERAL', 'DEPARTMENT_USER_LIST'),
        ('ADMIN_GENERAL', 'DEPARTMENT_USER_INSERT'),
        ('ADMIN_GENERAL', 'DEPARTMENT_USER_UPDATE'),
        ('ADMIN_GENERAL', 'DEPARTMENT_USER_DELETE'),

        ('ADMIN_GENERAL', 'DOCUMENT_LIST'),
        ('ADMIN_GENERAL', 'DOCUMENT_INSERT'),
        ('ADMIN_GENERAL', 'DOCUMENT_UPDATE'),
        ('ADMIN_GENERAL', 'DOCUMENT_DELETE'),

        ('ADMIN_GENERAL', 'DOCUMENT_DEPARTMENT_LIST'),
        ('ADMIN_GENERAL', 'DOCUMENT_DEPARTMENT_INSERT'),
        ('ADMIN_GENERAL', 'DOCUMENT_DEPARTMENT_UPDATE'),
        ('ADMIN_GENERAL', 'DOCUMENT_DEPARTMENT_DELETE'),

        ('ADMIN_GENERAL', 'DOCUMENT_USER_LIST'),
        ('ADMIN_GENERAL', 'DOCUMENT_USER_INSERT'),
        ('ADMIN_GENERAL', 'DOCUMENT_USER_UPDATE'),
        ('ADMIN_GENERAL', 'DOCUMENT_USER_DELETE'),

        ('ADMIN_GENERAL', 'PERMISSION_LIST'),
        ('ADMIN_GENERAL', 'PERMISSION_INSERT'),
        ('ADMIN_GENERAL', 'PERMISSION_UPDATE'),
        ('ADMIN_GENERAL', 'PERMISSION_DELETE'),

        ('ADMIN_GENERAL', 'PERMISSION_USER_LIST'),
        ('ADMIN_GENERAL', 'PERMISSION_USER_INSERT'),
        ('ADMIN_GENERAL', 'PERMISSION_USER_UPDATE'),
        ('ADMIN_GENERAL', 'PERMISSION_USER_DELETE'),

        ('ADMIN_GENERAL', 'PUBLICATION_LIST'),
        ('ADMIN_GENERAL', 'PUBLICATION_INSERT'),
        ('ADMIN_GENERAL', 'PUBLICATION_UPDATE'),
        ('ADMIN_GENERAL', 'PUBLICATION_DELETE'),

        ('ADMIN_GENERAL', 'PUBLICATION_DEPARTMENT_LIST'),
        ('ADMIN_GENERAL', 'PUBLICATION_DEPARTMENT_INSERT'),
        ('ADMIN_GENERAL', 'PUBLICATION_DEPARTMENT_UPDATE'),
        ('ADMIN_GENERAL', 'PUBLICATION_DEPARTMENT_DELETE'),

        ('ADMIN_GENERAL', 'PUBLICATION_USER_LIST'),
        ('ADMIN_GENERAL', 'PUBLICATION_USER_INSERT'),
        ('ADMIN_GENERAL', 'PUBLICATION_USER_UPDATE'),
        ('ADMIN_GENERAL', 'PUBLICATION_USER_DELETE'),

        ('ADMIN_GENERAL', 'ROLE_LIST'),
        ('ADMIN_GENERAL', 'ROLE_INSERT'),
        ('ADMIN_GENERAL', 'ROLE_UPDATE'),
        ('ADMIN_GENERAL', 'ROLE_DELETE'),

        ('ADMIN_GENERAL', 'ROLE_PERMISSION_LIST'),
        ('ADMIN_GENERAL', 'ROLE_PERMISSION_INSERT'),
        ('ADMIN_GENERAL', 'ROLE_PERMISSION_UPDATE'),
        ('ADMIN_GENERAL', 'ROLE_PERMISSION_DELETE'),

        ('ADMIN_GENERAL', 'ROLE_USER_LIST'),
        ('ADMIN_GENERAL', 'ROLE_USER_INSERT'),
        ('ADMIN_GENERAL', 'ROLE_USER_UPDATE'),
        ('ADMIN_GENERAL', 'ROLE_USER_DELETE'),

        -- DOCUMENT_VIEW
        ('DOCUMENT_VIEW', 'DOCUMENT_LIST'),

        -- DOCUMENT_USER
        ('DOCUMENT_USER', 'DOCUMENT_LIST'),
        ('DOCUMENT_USER', 'DOCUMENT_INSERT'),
        ('DOCUMENT_USER', 'DOCUMENT_UPDATE'),
        ('DOCUMENT_USER', 'DOCUMENT_DELETE'),

        -- DOCUMENT_ADMIN
        ('DOCUMENT_ADMIN', 'DOCUMENT_LIST'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_INSERT'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_UPDATE'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_DELETE'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_USER_LIST'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_USER_INSERT'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_USER_UPDATE'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_USER_DELETE'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_DEPARTMENT_LIST'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_DEPARTMENT_INSERT'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_DEPARTMENT_UPDATE'),
        ('DOCUMENT_ADMIN', 'DOCUMENT_DEPARTMENT_DELETE'),

        -- PUBLICATION_VIEW
        ('PUBLICATION_VIEW', 'PUBLICATION_LIST'),

        -- PUBLICATION_USER
        ('PUBLICATION_USER', 'PUBLICATION_LIST'),
        ('PUBLICATION_USER', 'PUBLICATION_INSERT'),
        ('PUBLICATION_USER', 'PUBLICATION_UPDATE'),
        ('PUBLICATION_USER', 'PUBLICATION_DELETE'),

        -- PUBLICATION_ADMIN
        ('PUBLICATION_ADMIN', 'PUBLICATION_LIST'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_INSERT'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_UPDATE'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_DELETE'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_USER_LIST'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_USER_INSERT'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_USER_UPDATE'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_USER_DELETE'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_DEPARTMENT_LIST'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_DEPARTMENT_INSERT'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_DEPARTMENT_UPDATE'),
        ('PUBLICATION_ADMIN', 'PUBLICATION_DEPARTMENT_DELETE')
)
INSERT INTO PUBLIC.ROLE_PERMISSION (
      ROLE_ID
    , PERMISSION_ID
    , ASSIGNED_AT
)
SELECT
      R.ID
    , P.ID
    , NOW()
FROM ROLE_PERMISSION_SEED S
INNER JOIN PUBLIC.ROLE R
    ON R.CODE = S.ROLE_CODE
INNER JOIN PUBLIC.PERMISSION P
    ON P.CODE = S.PERMISSION_CODE
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.ROLE_PERMISSION RP
    WHERE RP.ROLE_ID = R.ID
      AND RP.PERMISSION_ID = P.ID
);

COMMIT;
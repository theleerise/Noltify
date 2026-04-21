BEGIN;

-- =========================================================
-- Datos de prueba
-- Password comun: 123456
-- =========================================================

-- =========================================================
-- DEPARTMENT
-- =========================================================
WITH DEPARTMENT_SEED (
    CODE,
    NAME,
    DESCRIPTION,
    IS_ACTIVE
) AS (
    VALUES
        ('DIRECTION', 'Direccion', 'Departamento de direccion y supervision global.', TRUE),
        ('IT', 'Tecnologia', 'Departamento tecnico para sistemas, soporte y desarrollo.', TRUE),
        ('HR', 'Recursos Humanos', 'Departamento de gestion de personas y talento.', TRUE),
        ('FINANCE', 'Finanzas', 'Departamento de contabilidad, tesoreria y control presupuestario.', TRUE),
        ('OPERATIONS', 'Operaciones', 'Departamento de coordinacion operativa y procesos internos.', TRUE),
        ('COMMUNICATION', 'Comunicacion', 'Departamento de contenidos, publicaciones y difusion.', TRUE),
        ('LEGAL', 'Legal', 'Departamento de validacion normativa y documentacion contractual.', TRUE),
        ('ARCHIVE', 'Archivo', 'Departamento de custodia documental y archivo historico.', TRUE)
)
INSERT INTO PUBLIC.DEPARTMENT (
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
    , S.IS_ACTIVE
    , NOW()
    , NOW()
FROM DEPARTMENT_SEED S
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.DEPARTMENT D
    WHERE UPPER(D.CODE) = UPPER(S.CODE)
);

-- =========================================================
-- APP_USER
-- =========================================================
WITH USER_SEED (
    USERNAME,
    EMAIL,
    PASSWORD_HASH,
    FIRST_NAME,
    LAST_NAME,
    IS_ACTIVE,
    IS_SUPERUSER
) AS (
    VALUES
        ('sofia.example', 'sofia.example@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Sofia', 'Superusuario', TRUE, TRUE),
        ('marcos.root', 'marcos.root@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Marcos', 'Root', TRUE, TRUE),
        ('adrian.example', 'adrian.example@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Adrian', 'Admin General', TRUE, FALSE),
        ('diana.example', 'diana.example@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Diana', 'Documentos', TRUE, FALSE),
        ('paula.example', 'paula.example@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Paula', 'Publicaciones', TRUE, FALSE),
        ('carla.example', 'carla.example@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Carla', 'Colaboradora', TRUE, FALSE),
        ('lucas.viewer', 'lucas.viewer@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Lucas', 'Visualizador', TRUE, FALSE),
        ('nora.viewer', 'nora.viewer@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Nora', 'Comunicacion', TRUE, FALSE),
        ('mario.mixed', 'mario.mixed@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Mario', 'Mixto', TRUE, FALSE),
        ('irene.hr', 'irene.hr@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Irene', 'People Ops', TRUE, FALSE),
        ('sergio.inactive', 'sergio.inactive@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Sergio', 'Inactivo', FALSE, FALSE),
        ('laura.finance', 'laura.finance@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Laura', 'Finanzas', TRUE, FALSE),
        ('diego.legal', 'diego.legal@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Diego', 'Legal', TRUE, FALSE),
        ('alba.archive', 'alba.archive@noltify.com', 'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=', 'Alba', 'Archivo', TRUE, FALSE)
)
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
)
SELECT
      S.USERNAME
    , S.EMAIL
    , S.PASSWORD_HASH
    , S.FIRST_NAME
    , S.LAST_NAME
    , S.IS_ACTIVE
    , S.IS_SUPERUSER
    , NOW()
    , NOW()
FROM USER_SEED S
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.APP_USER U
    WHERE UPPER(U.USERNAME) = UPPER(S.USERNAME)
       OR UPPER(U.EMAIL) = UPPER(S.EMAIL)
);

-- =========================================================
-- ROLE_USER
-- =========================================================
WITH ROLE_USER_SEED(USERNAME, ROLE_CODE) AS (
    VALUES
        ('adrian.example', 'ADMIN_GENERAL'),
        ('diana.example', 'DOCUMENT_ADMIN'),
        ('paula.example', 'PUBLICATION_ADMIN'),
        ('carla.example', 'DOCUMENT_USER'),
        ('carla.example', 'PUBLICATION_USER'),
        ('lucas.viewer', 'DOCUMENT_VIEW'),
        ('nora.viewer', 'PUBLICATION_VIEW'),
        ('mario.mixed', 'DOCUMENT_ADMIN'),
        ('mario.mixed', 'PUBLICATION_USER'),
        ('irene.hr', 'ADMIN_GENERAL'),
        ('sergio.inactive', 'DOCUMENT_USER'),
        ('laura.finance', 'DOCUMENT_VIEW'),
        ('laura.finance', 'PUBLICATION_VIEW'),
        ('diego.legal', 'DOCUMENT_VIEW'),
        ('alba.archive', 'DOCUMENT_USER')
)
INSERT INTO PUBLIC.ROLE_USER (
      USER_ID
    , ROLE_ID
    , ASSIGNED_AT
)
SELECT
      U.ID
    , R.ID
    , NOW()
FROM ROLE_USER_SEED S
INNER JOIN PUBLIC.APP_USER U
    ON UPPER(U.USERNAME) = UPPER(S.USERNAME)
INNER JOIN PUBLIC.ROLE R
    ON UPPER(R.CODE) = UPPER(S.ROLE_CODE)
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.ROLE_USER RU
    WHERE RU.USER_ID = U.ID
      AND RU.ROLE_ID = R.ID
);

-- =========================================================
-- DEPARTMENT_USER
-- =========================================================
WITH DEPARTMENT_USER_SEED(USERNAME, DEPARTMENT_CODE) AS (
    VALUES
        ('sofia.example', 'DIRECTION'),
        ('sofia.example', 'IT'),
        ('marcos.root', 'DIRECTION'),
        ('marcos.root', 'LEGAL'),
        ('adrian.example', 'OPERATIONS'),
        ('adrian.example', 'HR'),
        ('diana.example', 'IT'),
        ('diana.example', 'ARCHIVE'),
        ('paula.example', 'COMMUNICATION'),
        ('paula.example', 'OPERATIONS'),
        ('carla.example', 'COMMUNICATION'),
        ('carla.example', 'ARCHIVE'),
        ('lucas.viewer', 'ARCHIVE'),
        ('nora.viewer', 'COMMUNICATION'),
        ('mario.mixed', 'IT'),
        ('mario.mixed', 'COMMUNICATION'),
        ('irene.hr', 'HR'),
        ('irene.hr', 'DIRECTION'),
        ('sergio.inactive', 'OPERATIONS'),
        ('laura.finance', 'FINANCE'),
        ('laura.finance', 'DIRECTION'),
        ('diego.legal', 'LEGAL'),
        ('alba.archive', 'ARCHIVE')
)
INSERT INTO PUBLIC.DEPARTMENT_USER (
      DEPARTMENT_ID
    , USER_ID
    , ASSIGNED_AT
)
SELECT
      D.ID
    , U.ID
    , NOW()
FROM DEPARTMENT_USER_SEED S
INNER JOIN PUBLIC.APP_USER U
    ON UPPER(U.USERNAME) = UPPER(S.USERNAME)
INNER JOIN PUBLIC.DEPARTMENT D
    ON UPPER(D.CODE) = UPPER(S.DEPARTMENT_CODE)
WHERE NOT EXISTS (
    SELECT 1
    FROM PUBLIC.DEPARTMENT_USER DU
    WHERE DU.DEPARTMENT_ID = D.ID
      AND DU.USER_ID = U.ID
);

COMMIT;

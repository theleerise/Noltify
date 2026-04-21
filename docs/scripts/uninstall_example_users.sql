BEGIN;

-- =========================================================
-- Usuarios objetivo
-- =========================================================
WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.PERMISSION_USER PU
WHERE PU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.ROLE_USER RU
WHERE RU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.DEPARTMENT_USER DU
WHERE DU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.DOCUMENT_USER DU
WHERE DU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.PUBLICATION_USER PU
WHERE PU.USER_ID IN (SELECT ID FROM TARGET_USERS);

-- Si quieres conservar documentos/publicaciones creados por estos usuarios, comenta estos dos bloques
WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.DOCUMENT
WHERE UPLOADED_BY IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.PUBLICATION
WHERE CREATED_BY IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('marcos.root'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example'),
        UPPER('lucas.viewer'),
        UPPER('nora.viewer'),
        UPPER('mario.mixed'),
        UPPER('irene.hr'),
        UPPER('sergio.inactive'),
        UPPER('laura.finance'),
        UPPER('diego.legal'),
        UPPER('alba.archive')
    )
)
DELETE FROM PUBLIC.APP_USER
WHERE ID IN (SELECT ID FROM TARGET_USERS);

-- =========================================================
-- Departamentos objetivo
-- =========================================================
WITH TARGET_DEPARTMENTS AS (
    SELECT ID, CODE
    FROM PUBLIC.DEPARTMENT
    WHERE UPPER(CODE) IN (
        UPPER('DIRECTION'),
        UPPER('IT'),
        UPPER('HR'),
        UPPER('FINANCE'),
        UPPER('OPERATIONS'),
        UPPER('COMMUNICATION'),
        UPPER('LEGAL'),
        UPPER('ARCHIVE')
    )
)
DELETE FROM PUBLIC.DEPARTMENT
WHERE ID IN (SELECT ID FROM TARGET_DEPARTMENTS);

COMMIT;

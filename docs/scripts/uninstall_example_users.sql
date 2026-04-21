BEGIN;

-- =========================================================
-- Usuarios objetivo
-- =========================================================
WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.PERMISSION_USER PU
WHERE PU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.ROLE_USER RU
WHERE RU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.DEPARTMENT_USER DU
WHERE DU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.DOCUMENT_USER DU
WHERE DU.USER_ID IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
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
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.DOCUMENT
WHERE UPLOADED_BY IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.PUBLICATION
WHERE CREATED_BY IN (SELECT ID FROM TARGET_USERS);

WITH TARGET_USERS AS (
    SELECT ID, USERNAME
    FROM PUBLIC.APP_USER
    WHERE UPPER(USERNAME) IN (
        UPPER('sofia.example'),
        UPPER('adrian.example'),
        UPPER('diana.example'),
        UPPER('paula.example'),
        UPPER('carla.example')
    )
)
DELETE FROM PUBLIC.APP_USER
WHERE ID IN (SELECT ID FROM TARGET_USERS);

COMMIT;

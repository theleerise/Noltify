BEGIN;

-- =========================================================
-- APP_USER
-- Password comun: 123456
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
        (
            'sofia.example',
            'sofia.example@noltify.com',
            'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=',
            'Sofia',
            'Superusuario',
            TRUE,
            TRUE
        ),
        (
            'adrian.example',
            'adrian.example@noltify.com',
            'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=',
            'Adrian',
            'Admin General',
            TRUE,
            FALSE
        ),
        (
            'diana.example',
            'diana.example@noltify.com',
            'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=',
            'Diana',
            'Documentos',
            TRUE,
            FALSE
        ),
        (
            'paula.example',
            'paula.example@noltify.com',
            'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=',
            'Paula',
            'Publicaciones',
            TRUE,
            FALSE
        ),
        (
            'carla.example',
            'carla.example@noltify.com',
            'pbkdf2_sha256$1200000$gWCdgIsli5FULm1uyQkjro$v3H50CiKqUP+nFarGUe7WODWSYupREhz7aOk9DSq3Eo=',
            'Carla',
            'Colaboradora',
            TRUE,
            FALSE
        )
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
        ('carla.example', 'PUBLICATION_USER')
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

COMMIT;

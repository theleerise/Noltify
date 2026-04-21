# Noltify

Noltify es una aplicacion web construida con Django para gestionar documentos, publicaciones internas, usuarios, departamentos, roles y permisos.

La aplicacion usa Django como capa web, Jinja2 para las plantillas y PostgreSQL como base de datos principal. El modelo funcional del negocio no se crea con migraciones de Django: se prepara con scripts SQL incluidos en `docs/`.

## Funcionalidades

- Inicio de sesion con usuario o email.
- Gestion de usuarios y perfiles.
- Gestion de departamentos y asignaciones de usuarios.
- Gestion de roles, permisos y relaciones entre ambos.
- Gestion de documentos y asignacion a usuarios o departamentos.
- Gestion de publicaciones/notificaciones y asignacion a usuarios o departamentos.
- Panel inicial condicionado por permisos del usuario autenticado.

## Stack tecnico

- Python 3.12
- Django 5
- Jinja2
- PostgreSQL
- `psycopg` y `psycopg_pool`
- WhiteNoise para archivos estaticos
- Gunicorn para despliegue
- Docker para empaquetado opcional

## Estructura del proyecto

```text
.
|-- app/
|   |-- backend/        # vistas, managers, modelos y logica de acceso a datos
|   |-- config/         # settings, urls, ASGI y WSGI
|   `-- frontend/       # plantillas, macros, CSS, JS e imagenes
|-- docs/
|   |-- database_tables.sql
|   |-- permissions_and_roles.sql
|   |-- create_example_users.sql
|   `-- uninstall_example_users.sql
|-- media/
|-- staticfiles/
|-- manager.py          # punto de entrada principal de Django
|-- main.py             # arranque rapido para desarrollo
|-- requeriments.txt
|-- Dockerfile
`-- .env
```

## Requisitos previos

Antes de arrancar el proyecto conviene tener instalado:

- Python 3.12 o superior
- PostgreSQL 14 o superior
- `pip`
- Entorno virtual de Python recomendado
- Docker opcional, si quieres levantar la app en contenedor

## Variables de entorno

El proyecto carga automaticamente las variables desde el archivo `.env` situado en la raiz.

Ejemplo minimo:

```env
SECRET_KEY=django-insecure-change-this-key
DEBUG=1
USE_POSTGRES=1

ALLOWED_HOSTS=127.0.0.1,localhost,.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app

DB_NAME=noltify
DB_USER=noltify_app_user
DB_PASSWORD=88908890
DB_HOST=localhost
DB_PORT=5432
```

Notas:

- `USE_POSTGRES` aparece en el `.env`, pero actualmente la configuracion usa PostgreSQL de forma fija.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` existen en el archivo, aunque en `settings.py` se usan valores amplios para desarrollo.
- Para produccion cambia `SECRET_KEY`, desactiva `DEBUG` y revisa hosts/origenes permitidos.

## Instalacion completa en local

### 1. Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd Noltify
```

### 2. Crear el entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```powershell
pip install --upgrade pip
pip install -r requeriments.txt
```

### 4. Crear la base de datos PostgreSQL

Puedes crear la base y el usuario con `psql`. Ejemplo:

```sql
CREATE USER noltify_app_user WITH PASSWORD '88908890';
CREATE DATABASE noltify OWNER noltify_app_user;
GRANT ALL PRIVILEGES ON DATABASE noltify TO noltify_app_user;
```

Si prefieres otros valores, actualiza tambien el archivo `.env`.

### 5. Preparar el archivo `.env`

Si no existe, crea `.env` en la raiz del proyecto y ajusta al menos:

- `SECRET_KEY`
- `DEBUG`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

### 6. Crear el esquema de negocio

Este proyecto utiliza scripts SQL manuales para crear sus tablas principales.

Ejecuta los scripts en este orden:

1. `docs/scripts/database_tables.sql`
2. `docs/scripts/permissions_and_roles.sql`
3. `docs/scripts/create_example_users.sql` opcional, solo si quieres datos de prueba

Ejemplo con `psql`:

```powershell
psql -U noltify_app_user -d noltify -h localhost -f docs/scripts/database_tables.sql
psql -U noltify_app_user -d noltify -h localhost -f docs/scripts/permissions_and_roles.sql
psql -U noltify_app_user -d noltify -h localhost -f docs/scripts/create_example_users.sql
```

### 7. Ejecutar Django

Opcion recomendada:

```powershell
.\.venv\Scripts\python.exe manager.py runserver
```

Tambien puedes usar:

```powershell
.\.venv\Scripts\python.exe main.py
```

Por defecto la aplicacion quedara disponible en:

```text
http://127.0.0.1:8000/
```

### 8. Acceder a la aplicacion

La aplicacion redirige al login si no hay sesion iniciada.

El superusuario que se crea por defecto es el usuario

- `superusuario` ccon la contraseña por defecto `123456`

Si cargaste los datos de ejemplo, puedes entrar con cualquiera de estos usuarios:

- `sofia.example`
- `adrian.example`
- `diana.example`
- `paula.example`
- `carla.example`

Contrasena comun de los usuarios de ejemplo:

```text
123456
```

Tambien puedes iniciar sesion usando el email en lugar del nombre de usuario.

## Scripts SQL incluidos

### `docs/database_tables.sql`

Crea las tablas principales:

- `APP_USER`
- `PERMISSION`
- `PERMISSION_USER`
- `ROLE`
- `ROLE_PERMISSION`
- `ROLE_USER`
- `DEPARTMENT`
- `DEPARTMENT_USER`
- `PUBLICATION`
- `PUBLICATION_DEPARTMENT`
- `PUBLICATION_USER`
- `DOCUMENT`
- `DOCUMENT_USER`
- `DOCUMENT_DEPARTMENT`

### `docs/permissions_and_roles.sql`

Inserta el catalogo base de permisos y roles, incluyendo perfiles como:

- `ADMIN_GENERAL`
- `DOCUMENT_VIEW`
- `DOCUMENT_USER`
- `DOCUMENT_ADMIN`
- `PUBLICATION_VIEW`
- `PUBLICATION_USER`
- `PUBLICATION_ADMIN`

### `docs/create_example_users.sql`

Inserta usuarios de ejemplo y asigna roles iniciales.

### `docs/uninstall_example_users.sql`

Elimina los usuarios de ejemplo y sus relaciones. Tambien puede eliminar documentos y publicaciones creadas por esos usuarios, segun el propio script.

## Comandos utiles

Comprobar configuracion basica del proyecto:

```powershell
.\.venv\Scripts\python.exe manager.py check
```

Recopilar estaticos:

```powershell
.\.venv\Scripts\python.exe manager.py collectstatic --noinput
```

## Despliegue con Docker

El repositorio incluye un `Dockerfile` listo para construir la aplicacion.

### Construccion

```powershell
docker build -t noltify .
```

### Ejecucion

```powershell
docker run --rm -p 8080:8080 --env-file .env noltify
```

Notas importantes para Docker:

- El contenedor ejecuta `collectstatic` al arrancar.
- El servidor de aplicacion expone el puerto `8080`.
- La base de datos PostgreSQL debe existir y ser accesible desde el contenedor.
- Los scripts SQL de `docs/` no se ejecutan automaticamente: la base debe estar preparada antes.

## Consideraciones importantes

- No hay migraciones de Django para las entidades principales del negocio.
- El acceso a base de datos se hace mediante managers y consultas SQL directas.
- Las sesiones se almacenan en cookies firmadas, no en la tabla `django_session`.
- Si vas a desplegar en produccion, revisa seguridad, credenciales, hosts permitidos y politica de secretos.

## Solucion de problemas

### La app no arranca y falla la conexion a PostgreSQL

Revisa:

- que PostgreSQL este levantado
- que `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` sean correctos
- que la base exista
- que el usuario tenga permisos

### El login funciona pero faltan menus o vistas

Normalmente significa que el usuario no tiene roles o permisos asignados. Ejecuta `docs/permissions_and_roles.sql` y, si quieres un entorno listo para pruebas, `docs/create_example_users.sql`.

### La aplicacion carga pero faltan estilos

Ejecuta:

```powershell
.\.venv\Scripts\python.exe manager.py collectstatic --noinput
```

## Estado actual

En esta revision, el proyecto pasa correctamente el chequeo de Django:

```text
python manager.py check
System check identified no issues (0 silenced).
```

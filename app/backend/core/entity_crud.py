"""
Utilidades para construir vistas CRUD genéricas a partir de managers y modelos.

Este módulo permite generar de forma centralizada el conjunto habitual de
vistas necesarias para listar, obtener, crear, actualizar y eliminar registros
de una entidad, reduciendo la duplicidad de código en los distintos módulos de
vistas de la aplicación.
"""

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.core.authorization import build_crud_permission_map, require_any_permission
from backend.core.response import get_error_response, get_request_json, get_success_response


def build_crud_views(
    *,
    manager_class,
    model_class,
    template_prefix: str,
    singular_name: str,
    created_message: str,
    updated_message: str,
    deleted_message: str,
    not_found_message: str,
    permission_prefix: str | None = None,
):
    """
    Construye el conjunto estándar de vistas CRUD para una entidad.

    A partir de una clase manager, una clase de modelo y la configuración
    básica de nombres, plantillas y mensajes, este método genera las vistas
    necesarias para trabajar con una entidad de forma homogénea en toda la
    aplicación.

    Args:
        manager_class: Clase manager encargada de acceder a base de datos y
            ejecutar las operaciones CRUD de la entidad.
        model_class: Clase del modelo utilizada para validar, serializar y
            construir los datos de entrada y salida.
        template_prefix (str): Prefijo de plantillas donde se encuentran las
            vistas HTML de listado y formulario.
        singular_name (str): Nombre singular legible de la entidad, utilizado
            en algunos mensajes de respuesta.
        created_message (str): Mensaje que se devolverá cuando la creación del
            registro se complete correctamente.
        updated_message (str): Mensaje que se devolverá cuando la actualización
            del registro se complete correctamente.
        deleted_message (str): Mensaje que se devolverá cuando la eliminación
            del registro se complete correctamente.
        not_found_message (str): Mensaje que se devolverá cuando no exista el
            registro solicitado.
        permission_prefix (str | None): Prefijo base para construir el mapa de
            permisos CRUD. Si no se informa, las vistas se devolverán sin
            aplicar decoradores de permisos.

    Returns:
        dict: Diccionario que contiene las vistas CRUD generadas y listas para
        ser expuestas desde el módulo de URLs o desde un archivo de vistas.
    """

    @require_http_methods(["GET"])
    def list_view(request):
        """
        Renderiza la plantilla principal de listado de la entidad.

        Esta vista prepara la configuración serializada del modelo para que el
        frontend pueda construir dinámicamente columnas, filtros u otros
        elementos de interfaz asociados al listado.

        Args:
            request: Objeto request actual de Django.

        Returns:
            _type_: Respuesta HTML renderizada con la plantilla de listado.
        """
        context_page = {
            "entity_model": json.dumps(model_class.config())
        }
        return render(request, f"{template_prefix}/list.html", context_page)

    @require_http_methods(["GET"])
    def form_view(request):
        """
        Renderiza la plantilla del formulario de la entidad.

        Esta vista envía al frontend la configuración del modelo en formato
        diccionario para facilitar la construcción dinámica del formulario.

        Args:
            request: Objeto request actual de Django.

        Returns:
            _type_: Respuesta HTML renderizada con la plantilla del formulario.
        """
        context_page = {
            "entity_model": model_class.config()
        }
        return render(request, f"{template_prefix}/form.html", context_page)

    @require_http_methods(["GET"])
    def data(request):
        """
        Recupera un listado paginado de registros y lo devuelve en formato JSON.

        La vista lee los filtros, el orden y la página actual desde los
        parámetros GET, delega la consulta al manager correspondiente y
        devuelve la respuesta ya preparada para consumo del frontend.

        Args:
            request: Objeto request actual de Django.

        Returns:
            JsonResponse: Respuesta JSON con los datos paginados de la entidad o
            con la información de error si ocurre una excepción.
        """
        try:
            request_data = request.GET.dict()

            raw_filters = request_data.get("filters", "{}")
            filters = json.loads(raw_filters) if raw_filters else {}
            raw_orders = request_data.get("orders", "{}")
            orders = json.loads(raw_orders) if raw_orders else {}
            page = int(request_data.get("page", 1))

            mgr = manager_class()
            records = mgr.get_list_page(
                params=filters,
                order_by=orders,
                page=page,
                data_model=False
            )

            return JsonResponse(records, status=200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["GET"])
    def new_view(request):
        """
        Devuelve los datos iniciales necesarios para crear un nuevo registro.

        Esta vista obtiene desde el modelo un diccionario con valores por
        defecto para inicializar el formulario de alta en el frontend.

        Args:
            request: Objeto request actual de Django.

        Returns:
            JsonResponse: Respuesta JSON con los datos iniciales del formulario
            o con la descripción del error si la operación falla.
        """
        try:
            model_data = model_class.to_json_default_dict()
            return get_success_response(
                data=model_data,
                message="Datos iniciales obtenidos correctamente"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["GET"])
    def edit_view(request, id: int):
        """
        Recupera la información de un registro concreto para editarlo.

        La vista consulta el registro a partir de su identificador, valida su
        existencia y devuelve una represetación serializable que pueda ser
        cargada por el formulario de edición en el frontend.

        Args:
            request: Objeto request actual de Django.
            id (int): Identificador del registro que se desea editar.

        Returns:
            JsonResponse: Respuesta JSON con los datos del registro solicitado,
            con un error `404` si no existe o con un error general si falla el
            proceso.
        """
        try:
            mgr = manager_class()
            record = mgr.get_by_id(record_id=id, data_model=False)

            if not record:
                return get_error_response(error=not_found_message, status=404)

            if isinstance(record, model_class):
                record = record.to_json_dict()
            else:
                record = model_class.serialize_record(record)

            return get_success_response(
                data=record,
                message=f"{singular_name} obtenido correctamente"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["POST"])
    def create(request):
        """
        Crea un nuevo registro de la entidad a partir de la petición recibida.

        La vista toma los datos enviados por el cliente, construye una instancia
        del modelo para validarlos y después delega la inserción al manager.

        Args:
            request: Objeto request actual de Django.

        Returns:
            JsonResponse: Respuesta JSON con el resultado de la creación o con
            la información del error si la operación no puede completarse.
        """
        try:
            request_data = get_request_json(request)
            data = request_data.get("data", {})
            model = model_class(**data)

            mgr = manager_class()
            result = mgr.insert_query(model.to_insert_dict())

            return get_success_response(
                data=result,
                message=created_message,
                status=201
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["PUT"])
    def update(request, id: int):
        """
        Actualiza un registro existente de la entidad.

        La vista obtiene los datos enviados por el cliente, incorpora el
        identificador recibido por URL, valida el contenido mediante el modelo y
        delega la actualización al manager correspondiente.

        Args:
            request: Objeto request actual de Django.
            id (int): Identificador del registro que se desea actualizar.

        Returns:
            JsonResponse: Respuesta JSON con el resultado de la actualización o
            con la información de error si el proceso falla.
        """
        try:
            request_data = get_request_json(request)
            data = request_data.get("data", {})
            data["id"] = id
            model = model_class(**data)

            mgr = manager_class()
            result = mgr.update_query(model.to_update_dict(include_primary_key=True))

            return get_success_response(
                data=result,
                message=updated_message
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    @require_http_methods(["DELETE"])
    def delete(request, id: int):
        """
        Elimina un registro de la entidad a partir de su identificador.

        La vista construye el parámetro mínimo necesario para la operación de
        borrado y delega la eliminación al manager.

        Args:
            request: Objeto request actual de Django.
            id (int): Identificador del registro que se desea eliminar.

        Returns:
            JsonResponse: Respuesta JSON con el resultado de la eliminación o
            con la información de error correspondiente.
        """
        try:
            mgr = manager_class()
            params = {mgr.primary_key: id}
            result = mgr.delete_query(params)

            return get_success_response(
                data=result,
                message=deleted_message
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_error_response(str(e))

    views = {
        "list_view": list_view,
        "form_view": form_view,
        "data": data,
        "new_view": new_view,
        "edit_view": edit_view,
        "create": create,
        "update": update,
        "delete": delete,
    }

    if not permission_prefix:
        return views

    permission_map = build_crud_permission_map(permission_prefix)

    for view_name, permission_codes in permission_map.items():
        views[view_name] = require_any_permission(*permission_codes)(views[view_name])

    return views
